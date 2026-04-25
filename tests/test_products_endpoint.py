"""
Tests for GET /api/v1/products.

Run:
    pytest tests/test_products_endpoint.py -v
"""

from __future__ import annotations

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from backend.main import app, Product

# ── fake row helper ─────────────────────────────────────────────
def _fake_row(
    id: int = 1,
    name: str = "SG3428XMP",
    category: str = "Switches",
    model: str = "SG3428XMP",
    specs_json: str | None = None,
    created_at: str = "2025-06-01T00:00:00",
) -> dict:
    if specs_json is None:
        specs_json = json.dumps({"poe_budget_w": 384, "total_ports": 24})
    return {
        "id": id,
        "name": name,
        "category": category,
        "model": model,
        "specs_json": specs_json,
        "created_at": created_at,
    }

# ── fixtures ─────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def mock_pool():
    """Return a mock asyncpg pool wired into app.state."""
    pool = AsyncMock()
    conn = AsyncMock()
    conn.fetchval = AsyncMock(return_value=2)
    conn.fetch = AsyncMock(return_value=[_fake_row(1), _fake_row(2, name="EAP670")])
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aexit__ = AsyncMock(return_value=False)
    app.state.pool = pool
    yield pool
    app.state.pool = None

@pytest_asyncio.fixture
async def client(mock_pool):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# ── tests ────────────────────────────────────────────────────────
@pytest.mark.asyncio
async def test_list_products_default(client):
    resp = await client.get("/api/v1/products")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    assert body["limit"] == 25
    assert body["offset"] == 0

@pytest.mark.asyncio
async def test_list_products_pagination(client):
    resp = await client.get("/api/v1/products?limit=1&offset=1")
    assert resp.status_code == 200
    body = resp.json()
    assert body["limit"] == 1
    assert body["offset"] == 1

@pytest.mark.asyncio
async def test_list_products_search(client):
    resp = await client.get("/api/v1/products?q=switch")
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_specs_json_parsed(client):
    resp = await client.get("/api/v1/products")
    item = resp.json()["items"][0]
    assert isinstance(item["specs"], dict)
    assert item["specs"]["poe_budget_w"] == 384

@pytest.mark.asyncio
async def test_limit_validation(client):
    resp = await client.get("/api/v1/products?limit=0")
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_limit_max(client):
    resp = await client.get("/api/v1/products?limit=200")
    assert resp.status_code == 422

@pytest.mark.asyncio
async def test_no_pool_returns_503():
    """When pool is missing from app.state, should 503."""
    app.state.pool = None
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/products")
    assert resp.status_code == 503
