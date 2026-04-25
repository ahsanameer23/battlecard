import pytest
import uuid
import json
from httpx import AsyncClient, ASGITransport
from main import app, db_pool
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture
def mock_db(monkeypatch):
    mock_pool = MagicMock()
    mock_conn = AsyncMock()
    
    # Setup async context manager for db_pool.acquire()
    class AsyncContextManagerMock:
        async def __aenter__(self):
            return mock_conn
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    mock_pool.acquire.return_value = AsyncContextManagerMock()
    
    # Patch the global db_pool
    monkeypatch.setattr("main.db_pool", mock_pool)
    return mock_conn

@pytest.mark.asyncio
async def test_products_defaults(mock_db):
    mock_db.fetch.return_value = [
        {
            "id": uuid.uuid4(),
            "source": "competitor",
            "vendor": "Cisco",
            "model": "Catalyst 9300",
            "category": "Switches",
            "subcategory": "L3 Managed",
            "tier": "Enterprise",
            "price_usd": 3500.00,
            "specs_json": '{"quantitative": {"total_ports": 48}}',
            "data_completeness": 1.0,
            "created_at": "2026-04-25T10:00:00Z"
        }
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/products")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["vendor"] == "Cisco"
        assert data[0]["specs_json"]["quantitative"]["total_ports"] == 48

@pytest.mark.asyncio
async def test_products_pagination(mock_db):
    mock_db.fetch.return_value = []
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/products?limit=10&offset=20")
        assert response.status_code == 200
        # Verify the mock was called with correct limit and offset
        call_args = mock_db.fetch.call_args[0]
        assert call_args[2] == 10  # limit
        assert call_args[3] == 20  # offset

@pytest.mark.asyncio
async def test_products_search(mock_db):
    mock_db.fetch.return_value = []
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/products?q=Aruba")
        assert response.status_code == 200
        call_args = mock_db.fetch.call_args[0]
        assert "%Aruba%" in call_args[1]

@pytest.mark.asyncio
async def test_products_json_parsing(mock_db):
    # Test when specs_json is already a dict (asyncpg can return dicts for JSONB if configured)
    mock_db.fetch.return_value = [
        {
            "id": uuid.uuid4(),
            "source": "competitor",
            "vendor": "Juniper",
            "model": "EX4100",
            "category": "Switches",
            "tier": "Enterprise",
            "specs_json": {"quantitative": {"poe_budget_w": 740}},
            "data_completeness": 0.9,
        }
    ]
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/products")
        assert response.status_code == 200
        data = response.json()
        assert data[0]["specs_json"]["quantitative"]["poe_budget_w"] == 740

@pytest.mark.asyncio
async def test_products_validation():
    # Test validation error (limit > 1000)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/products?limit=2000")
        assert response.status_code == 422
        assert "less than or equal to 1000" in response.text
