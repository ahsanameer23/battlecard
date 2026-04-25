CREATE SCHEMA IF NOT EXISTS omada_nexus;

-- 1. TABLES & SCHEMA
CREATE TABLE IF NOT EXISTS omada_nexus.products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT NOT NULL CHECK (source IN ('internal', 'competitor')),
  vendor TEXT NOT NULL,
  model TEXT NOT NULL,
  category TEXT NOT NULL,
  subcategory TEXT,
  tier TEXT DEFAULT 'Enterprise',
  is_current BOOLEAN DEFAULT TRUE,
  price_usd NUMERIC(12,2),
  specs_json JSONB NOT NULL,
  data_completeness NUMERIC(3,2) DEFAULT 1.0,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE(vendor, model)
);

CREATE TABLE IF NOT EXISTS omada_nexus.match_weights (
  id SERIAL PRIMARY KEY,
  category TEXT NOT NULL,
  parameter TEXT NOT NULL,
  weight NUMERIC(6,5) NOT NULL CHECK (weight >= 0 AND weight <= 1),
  direction TEXT NOT NULL CHECK (direction IN ('symmetric','higher_is_better','lower_is_better')),
  UNIQUE(category, parameter)
);

CREATE TABLE IF NOT EXISTS omada_nexus.llm_tiebreak_cache (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  competitor_spec_hash TEXT NOT NULL,
  candidate_ids TEXT NOT NULL,
  winner_id UUID NOT NULL,
  sales_justification TEXT NOT NULL,
  UNIQUE(competitor_spec_hash, candidate_ids)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_products_internal ON omada_nexus.products(category, subcategory, tier) WHERE source = 'internal' AND is_current = true;
CREATE INDEX IF NOT EXISTS idx_products_specs_gin ON omada_nexus.products USING GIN (specs_json jsonb_path_ops);

-- 2. STAGE 1: HARD GATES (Candidate Retrieval)
CREATE OR REPLACE FUNCTION omada_nexus.get_candidates(
  p_category TEXT, p_subcategory TEXT DEFAULT NULL, p_tier TEXT DEFAULT NULL
)
RETURNS TABLE (id UUID, model TEXT, price_usd NUMERIC, specs_json JSONB)
LANGUAGE plpgsql STABLE AS $$
BEGIN
  RETURN QUERY
    SELECT ip.id, ip.model, ip.price_usd, ip.specs_json
    FROM omada_nexus.products ip
    WHERE ip.source = 'internal'
      AND ip.is_current = true
      AND ip.category = p_category
      AND (p_subcategory IS NULL OR ip.subcategory = p_subcategory)
      AND (p_tier IS NULL OR ip.tier = p_tier)
    ORDER BY ip.price_usd ASC;
END;
$$;

-- 3. STAGE 2: HARDENED CORE MATH
CREATE OR REPLACE FUNCTION omada_nexus.compute_weighted_similarity(
  target_json JSONB, internal_json JSONB, p_category TEXT
)
RETURNS NUMERIC LANGUAGE plpgsql STABLE AS $$
DECLARE
  total_score NUMERIC := 0; total_weight NUMERIC := 0; valid_weights NUMERIC;
  rec RECORD; target_val NUMERIC; internal_val NUMERIC; sim NUMERIC;
BEGIN
  FOR rec IN SELECT parameter, weight, direction FROM omada_nexus.match_weights WHERE category = p_category LOOP
    target_val   := (target_json -> 'quantitative' ->> rec.parameter)::NUMERIC;
    internal_val := (internal_json -> 'quantitative' ->> rec.parameter)::NUMERIC;

    CONTINUE WHEN target_val IS NULL; -- Missing competitor spec: skip & redistribute later

    IF internal_val IS NULL THEN 
      sim := 0.5; -- Missing internal spec: flat penalty
    ELSE
      CASE rec.direction
        WHEN 'symmetric' THEN sim := 1.0 - ABS(target_val - internal_val) / GREATEST(ABS(target_val), ABS(internal_val));
        WHEN 'higher_is_better' THEN
          IF internal_val >= target_val THEN sim := 1.0 - 0.2 * (internal_val - target_val) / internal_val;
          ELSE sim := 1.0 - (target_val - internal_val) / target_val; END IF;
        WHEN 'lower_is_better' THEN
          IF internal_val <= target_val THEN sim := 1.0 - 0.2 * (target_val - internal_val) / target_val;
          ELSE sim := 1.0 - (internal_val - target_val) / internal_val; END IF;
        ELSE sim := 0.0;
      END CASE;
    END IF;

    total_score  := total_score + sim * rec.weight;
    total_weight := total_weight + rec.weight;
  END LOOP;

  IF total_weight = 0 THEN RETURN 0; END IF;

  valid_weights := (SELECT COALESCE(SUM(weight),0) FROM omada_nexus.match_weights WHERE category = p_category);
  total_score := total_score * (valid_weights / total_weight) * 100.0;
  
  RETURN GREATEST(0, LEAST(100, ROUND(total_score, 2)));
END;
$$;

-- 4. SEED DATA (Weights for Switches)
INSERT INTO omada_nexus.match_weights (category, parameter, weight, direction) VALUES
('Switches','poe_budget_w', 0.35, 'higher_is_better'),
('Switches','total_ports', 0.20, 'symmetric'),
('Switches','uplink_speed_gbps', 0.15, 'higher_is_better'),
('Switches','poe_ports', 0.15, 'symmetric'),
('Switches','switching_capacity_gbps', 0.10, 'higher_is_better'),
('Switches','max_power_consumption_w', 0.05, 'lower_is_better')
ON CONFLICT DO NOTHING;
