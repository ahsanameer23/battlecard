# pyrefly: ignore [missing-import]
import asyncio, asyncpg, os, sys
sys.path.insert(0, '.')
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv
load_dotenv('omada-nexus/.env')

url = os.getenv('DATABASE_URL')

FIX_SQL = """
CREATE OR REPLACE FUNCTION omada_nexus.compute_weighted_similarity(
  target_json JSONB, internal_json JSONB, p_category TEXT
)
RETURNS NUMERIC LANGUAGE plpgsql STABLE AS $$
DECLARE
  total_score  NUMERIC := 0;
  total_weight NUMERIC := 0;
  valid_weights NUMERIC;
  rec          RECORD;
  target_val   NUMERIC;
  internal_val NUMERIC;
  denom        NUMERIC;
  sim          NUMERIC;
BEGIN
  FOR rec IN
    SELECT parameter, weight, direction
    FROM omada_nexus.match_weights
    WHERE category = p_category
  LOOP
    target_val   := (target_json  -> 'quantitative' ->> rec.parameter)::NUMERIC;
    internal_val := (internal_json -> 'quantitative' ->> rec.parameter)::NUMERIC;

    CONTINUE WHEN target_val IS NULL;   -- skip missing competitor spec

    IF internal_val IS NULL THEN
      sim := 0.5;                       -- flat penalty for missing internal spec
    ELSE
      CASE rec.direction

        WHEN 'symmetric' THEN
          denom := GREATEST(ABS(target_val), ABS(internal_val));
          IF denom = 0 THEN
            sim := 1.0;                 -- both zero = perfect match
          ELSE
            sim := GREATEST(0.0, 1.0 - ABS(target_val - internal_val) / denom);
          END IF;

        WHEN 'higher_is_better' THEN
          IF internal_val >= target_val THEN
            denom := NULLIF(internal_val, 0);
            sim   := CASE WHEN denom IS NULL THEN 1.0
                          ELSE GREATEST(0.0, 1.0 - 0.2 * (internal_val - target_val) / denom) END;
          ELSE
            denom := NULLIF(target_val, 0);
            sim   := CASE WHEN denom IS NULL THEN 0.0
                          ELSE GREATEST(0.0, 1.0 - (target_val - internal_val) / denom) END;
          END IF;

        WHEN 'lower_is_better' THEN
          IF internal_val <= target_val THEN
            denom := NULLIF(target_val, 0);
            sim   := CASE WHEN denom IS NULL THEN 1.0
                          ELSE GREATEST(0.0, 1.0 - 0.2 * (target_val - internal_val) / denom) END;
          ELSE
            denom := NULLIF(internal_val, 0);
            sim   := CASE WHEN denom IS NULL THEN 0.0
                          ELSE GREATEST(0.0, 1.0 - (internal_val - target_val) / denom) END;
          END IF;

        ELSE
          sim := 0.0;
      END CASE;
    END IF;

    total_score  := total_score  + sim * rec.weight;
    total_weight := total_weight + rec.weight;
  END LOOP;

  IF total_weight = 0 THEN
    RETURN 50;   -- no weights for category -> neutral score
  END IF;

  valid_weights := COALESCE(
    (SELECT SUM(weight) FROM omada_nexus.match_weights WHERE category = p_category), 0
  );

  total_score := total_score * (valid_weights / total_weight) * 100.0;
  RETURN GREATEST(0, LEAST(100, ROUND(total_score, 2)));
END;
$$;
"""

SMOKE_ZERO = """
SELECT omada_nexus.compute_weighted_similarity(
  '{"quantitative": {"poe_budget_w": 0, "total_ports": 0}}'::jsonb,
  '{"quantitative": {"poe_budget_w": 0, "total_ports": 48}}'::jsonb,
  'Switches'
)
"""

SMOKE_NORMAL = """
SELECT omada_nexus.compute_weighted_similarity(
  '{"quantitative": {"poe_budget_w": 370, "total_ports": 48, "uplink_speed_gbps": 10}}'::jsonb,
  '{"quantitative": {"poe_budget_w": 400, "total_ports": 48, "uplink_speed_gbps": 10}}'::jsonb,
  'Switches'
)
"""

async def apply():
    conn = await asyncpg.connect(url)
    await conn.execute(FIX_SQL)
    print("Function patched successfully!")

    t1 = await conn.fetchval(SMOKE_ZERO)
    print(f"Smoke test (both zeros):  {t1}")

    t2 = await conn.fetchval(SMOKE_NORMAL)
    print(f"Smoke test (normal vals): {t2}")

    await conn.close()

asyncio.run(apply())
