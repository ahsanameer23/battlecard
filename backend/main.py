"""
omada-nexus FastAPI backend — product catalog endpoint.

Run:
    uvicorn backend.main:app --reload --port 8000
"""

from __future__ import annotations

import json
import os
from contextlib import asynccontextmanager
from typing import Any

import asyncpg
from dotenv import load_dotenv
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

# ── env ──────────────────────────────────────────────────────────
load_dotenv("omada-nexus/.env")
DATABASE_URL: str = os.getenv("DATABASE_URL", "")

# ── models ───────────────────────────────────────────────────────
class Product(BaseModel):
    id: int
    name: str
    category: str | None = None
    model: str | None = None
    specs: dict[str, Any] | None = None
    created_at: str | None = None

class ProductListResponse(BaseModel):
    items: list[Product]
    total: int
    limit: int
    offset: int

# ── pool accessor (app.state) ───────────────────────────────────
def get_pool(app: FastAPI) -> asyncpg.Pool:
    pool = getattr(app.state, "pool", None)
    if pool is None:
        raise HTTPException(status_code=503, detail="DB pool not ready")
    return pool

# ── lifespan ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await asyncpg.create_pool(
        DATABASE_URL, min_size=2, max_size=10
    )
    yield
    await app.state.pool.close()

app = FastAPI(
    title="omada-nexus API",
    version="0.1.0",
    lifespan=lifespan,
)

# ── helpers ──────────────────────────────────────────────────────
def _parse_specs(raw: str | None) -> dict[str, Any] | None:
    """Parse specs_json TEXT/JSONB column into a Python dict."""
    if raw is None:
        return None
    if isinstance(raw, dict):
        return raw
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None

def _row_to_product(row: asyncpg.Record) -> Product:
    return Product(
        id=row["id"],
        name=row["name"],
        category=row.get("category"),
        model=row.get("model"),
        specs=_parse_specs(row.get("specs_json")),
        created_at=str(row["created_at"]) if row.get("created_at") else None,
    )

# ── endpoint ─────────────────────────────────────────────────────

@app.get("/api/v1/products", response_model=ProductListResponse)
async def list_products(
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    q: str | None = Query(default=None, max_length=200),
):
    pool = get_pool(app)
    async with pool.acquire() as conn:
        where = ""
        args: list[Any] = []
        if q:
            where = "WHERE p.name ILIKE $1 OR p.category ILIKE $1"
            args.append(f"%{q}%")

        count_sql = f"SELECT COUNT(*) FROM omada_nexus.products p {where}"
        total: int = await conn.fetchval(count_sql, *args)

        idx = len(args) + 1
        data_sql = (
            f"SELECT * FROM omada_nexus.products p {where} "
            f"ORDER BY p.id LIMIT ${idx} OFFSET ${idx + 1}"
        )
        args.extend([limit, offset])
        rows = await conn.fetch(data_sql, *args)

    return ProductListResponse(
        items=[_row_to_product(r) for r in rows],
        total=total,
        limit=limit,
        offset=offset,
    )
