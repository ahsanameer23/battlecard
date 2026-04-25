import os, json, hashlib, shutil, tempfile, uuid
from contextlib import asynccontextmanager
from typing import List, Optional

import asyncpg
from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form, Query
from pydantic import BaseModel
from dotenv import load_dotenv
from ingestion import extract_text_from_pdf, extract_specs_with_ollama

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

db_pool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool
    db_pool = await asyncpg.create_pool(DB_URL, min_size=2, max_size=10)
    yield
    await db_pool.close()

app = FastAPI(title="Omada Nexus API", version="1.0.0", lifespan=lifespan)

# =====================================================================
# 1. STAGE 0: PDF INGESTION ENDPOINT
# =====================================================================
@app.post("/api/v1/ingest", status_code=202)
async def ingest_datasheet(
    background_tasks: BackgroundTasks, file: UploadFile = File(...), 
    vendor: str = Form(...), model: str = Form(...), category: str = Form(...), 
    subcategory: Optional[str] = Form(None), price_usd: Optional[float] = Form(None), 
    tier: str = Form("Enterprise")
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Must be a PDF.")

    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    with open(temp_pdf.name, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    async def process_pdf():
        try:
            raw_text = extract_text_from_pdf(temp_pdf.name)
            specs = extract_specs_with_ollama(raw_text)
            specs["ecosystem"] = {"omnisirus_managed": False} 

            q_fields = specs.get("quantitative", {})
            completeness = round(sum(1 for v in q_fields.values() if v is not None) / (len(q_fields) or 1), 2)

            async with db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO omada_nexus.products (source, vendor, model, category, subcategory, tier, price_usd, specs_json, data_completeness)
                    VALUES ('competitor', $1, $2, $3, $4, $5, $6, $7::jsonb, $8)
                    ON CONFLICT (vendor, model) DO UPDATE SET specs_json = EXCLUDED.specs_json, price_usd = EXCLUDED.price_usd
                """, vendor, model, category, subcategory, tier, price_usd, json.dumps(specs), completeness)
        finally:
            os.remove(temp_pdf.name)

    background_tasks.add_task(process_pdf)
    return {"status": "Accepted", "message": f"Datasheet queued for AI extraction."}

# =====================================================================
# 1.5 PRODUCTS ENDPOINT
# =====================================================================
class ProductOut(BaseModel):
    id: uuid.UUID
    source: str
    vendor: str
    model: str
    category: str
    subcategory: Optional[str] = None
    tier: str
    price_usd: Optional[float] = None
    specs_json: dict
    data_completeness: float

@app.get("/api/v1/products", response_model=List[ProductOut])
async def list_products(
    source: Optional[str] = 'competitor',
    limit: int = Query(100, le=1000), 
    offset: int = 0, 
    q: Optional[str] = None
):
    async with db_pool.acquire() as conn:
        if q:
            rows = await conn.fetch(
                """
                SELECT *
                FROM omada_nexus.products
                WHERE source = $1 AND (vendor ILIKE $2 OR model ILIKE $2)
                ORDER BY created_at DESC
                LIMIT $3 OFFSET $4
                """,
                source, f"%{q}%", limit, offset
            )
        else:
            rows = await conn.fetch(
                """
                SELECT *
                FROM omada_nexus.products
                WHERE source = $1
                ORDER BY created_at DESC
                LIMIT $2 OFFSET $3
                """,
                source, limit, offset
            )
            
        products = []
        for r in rows:
            prod = dict(r)
            if isinstance(prod.get('specs_json'), str):
                prod['specs_json'] = json.loads(prod['specs_json'])
            products.append(prod)
        return products

# =====================================================================
# 2. THE MATCH ORCHESTRATOR
# =====================================================================
class TieBreakerResult(BaseModel):
    winner_id: str
    sales_justification: str

@app.get("/api/v1/match/{competitor_id}")
async def generate_battle_card(competitor_id: str):
    async with db_pool.acquire() as conn:
        target = await conn.fetchrow("SELECT * FROM omada_nexus.products WHERE id = $1 AND source = 'competitor'", competitor_id)
        if not target: raise HTTPException(status_code=404, detail="Competitor not found")

        target_specs = json.loads(target['specs_json'])
        target_tier = target.get('tier', 'Enterprise')

        # Run Postgres Math (Stages 1 & 2)
        raw_cands = await conn.fetch("""
            SELECT c.id, c.model, c.price_usd, c.specs_json,
            omada_nexus.compute_weighted_similarity($1::jsonb, c.specs_json, $2) AS stage2_score
            FROM omada_nexus.get_candidates($2, $3, $4) c
        """, json.dumps(target_specs), target['category'], target['subcategory'], target_tier)

        # Stage 3: Python Business Modifiers
        scored_candidates = []
        for cand in raw_cands:
            c_specs = json.loads(cand['specs_json'])
            base_score = float(cand['stage2_score'] or 0)
            
            bool_bonus = sum(2.0 if c_specs.get("boolean_features", {}).get(k) else -2.0 
                             for k, v in target_specs.get("boolean_features", {}).items() if v)
            eco_mult = 1.05 if c_specs.get("ecosystem", {}).get("omnisirus_managed") else 1.0
            final_score = min(max((base_score + bool_bonus) * eco_mult, 0.0), 100.0)
            
            scored_candidates.append({
                "id": str(cand["id"]), "model": cand["model"], "price_usd": float(cand["price_usd"] or 0),
                "specs": c_specs, "stage2_base_score": base_score, "final_score": round(final_score, 2), 
                "sales_justification": None
            })

        ranked = sorted(scored_candidates, key=lambda x: x["final_score"], reverse=True)

        # Stage 4: Gemini Tie-Breaker Cache Check & Execution
        if len(ranked) >= 2 and (ranked[0]["final_score"] - ranked[1]["final_score"]) <= 2.0:
            spec_hash = hashlib.sha256(json.dumps(target_specs, sort_keys=True).encode()).hexdigest()
            cand_ids = ",".join(sorted([ranked[0]['id'], ranked[1]['id']]))
            cached = await conn.fetchrow("SELECT winner_id, sales_justification FROM omada_nexus.llm_tiebreak_cache WHERE competitor_spec_hash=$1 AND candidate_ids=$2", spec_hash, cand_ids)
            
            if cached:
                winner_id, justification = str(cached['winner_id']), cached['sales_justification']
            else:
                prompt = f"TARGET: {target['model']} ${target['price_usd']} {target_specs}. CAND A: {ranked[0]['model']} ${ranked[0]['price_usd']} {ranked[0]['specs']}. CAND B: {ranked[1]['model']} ${ranked[1]['price_usd']} {ranked[1]['specs']}. Break the tie ensuring price competitiveness."
                resp = ai_client.models.generate_content(
                    model='gemini-2.5-flash', contents=prompt,
                    config=types.GenerateContentConfig(response_mime_type="application/json", response_schema=TieBreakerResult, temperature=0.1)
                )
                winner_data = json.loads(resp.text)
                winner_id, justification = winner_data["winner_id"], winner_data["sales_justification"]
                await conn.execute("INSERT INTO omada_nexus.llm_tiebreak_cache (competitor_spec_hash, candidate_ids, winner_id, sales_justification) VALUES ($1, $2, $3::uuid, $4)", spec_hash, cand_ids, winner_id, justification)

            if winner_id == ranked[1]["id"]:
                ranked[0], ranked[1] = ranked[1], ranked[0]
            ranked[0]["sales_justification"] = justification

        return {"target_competitor": dict(target), "matches": ranked[:3]}

# =====================================================================
# 3. ADMIN ENDPOINTS: WEIGHT CONFIGURATION
# =====================================================================
class WeightUpdate(BaseModel):
    parameter: str
    weight: float

@app.get("/api/v1/weights/{category}")
async def get_weights(category: str):
    async with db_pool.acquire() as conn:
        rows = await conn.fetch("SELECT parameter, weight, direction FROM omada_nexus.match_weights WHERE category=$1", category)
        return [dict(r) for r in rows]

@app.put("/api/v1/weights/{category}")
async def update_weights(category: str, updates: List[WeightUpdate]):
    async with db_pool.acquire() as conn:
        async with conn.transaction():
            for u in updates:
                await conn.execute("UPDATE omada_nexus.match_weights SET weight=$1 WHERE category=$2 AND parameter=$3", u.weight, category, u.parameter)
    return {"status": "Success. Algorithm updated."}
