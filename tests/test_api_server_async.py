"""Test api_server with async methods via ApiSwitcher + smartasync."""

import asyncio
import pytest
from fastapi.testclient import TestClient
from smpub import PublishedClass, Publisher, ApiSwitcher
from smpub.api_server import create_fastapi_app


class AsyncTestHandler(PublishedClass):
    """Handler with async methods for testing HTTP server."""

    api = ApiSwitcher()

    def __init__(self):
        self.call_count = 0

    @api
    def sync_method(self, value: str) -> str:
        """Sync method."""
        self.call_count += 1
        return f"Sync: {value}"

    @api
    async def async_method(self, value: str) -> str:
        """Async method with smartasync."""
        await asyncio.sleep(0.01)
        self.call_count += 1
        return f"Async: {value}"

    @api
    async def async_with_default(self, value: str, count: int = 10) -> dict:
        """Async method with default parameter."""
        await asyncio.sleep(0.01)
        return {"value": value, "count": count}


class TestPublisher(Publisher):
    """Test publisher with async handler."""

    def initialize(self):
        """Initialize with async handler."""
        handler = AsyncTestHandler()
        self.publish("test_handler", handler, cli=True, openapi=True)


@pytest.fixture
def fastapi_app():
    """Create FastAPI app with async handler."""
    publisher = TestPublisher()
    app = create_fastapi_app(publisher)
    return app


@pytest.fixture
def client(fastapi_app):
    """Create test client."""
    return TestClient(fastapi_app)


def test_sync_method_via_http(client):
    """Test that sync methods work via HTTP."""
    response = client.post(
        "/test_handler/sync_method", json={"value": "test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "Sync: test"


def test_async_method_via_http(client):
    """Test that async methods work via HTTP thanks to smartasync."""
    response = client.post(
        "/test_handler/async_method", json={"value": "test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == "Async: test"


def test_async_with_default_via_http_with_default(client):
    """Test async method with default parameter (using default)."""
    response = client.post(
        "/test_handler/async_with_default", json={"value": "test"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == {"value": "test", "count": 10}


def test_async_with_default_via_http_override(client):
    """Test async method with default parameter (overriding default)."""
    response = client.post(
        "/test_handler/async_with_default", json={"value": "test", "count": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == {"value": "test", "count": 5}


def test_multiple_async_calls_via_http(client):
    """Test multiple async HTTP calls work correctly."""
    # First call
    response1 = client.post(
        "/test_handler/async_method", json={"value": "first"}
    )
    assert response1.status_code == 200
    assert response1.json()["result"] == "Async: first"

    # Second call
    response2 = client.post(
        "/test_handler/async_method", json={"value": "second"}
    )
    assert response2.status_code == 200
    assert response2.json()["result"] == "Async: second"


def test_mixed_sync_async_via_http(client):
    """Test mixing sync and async calls via HTTP."""
    # Sync call
    response1 = client.post(
        "/test_handler/sync_method", json={"value": "sync"}
    )
    assert response1.status_code == 200
    assert response1.json()["result"] == "Sync: sync"

    # Async call
    response2 = client.post(
        "/test_handler/async_method", json={"value": "async"}
    )
    assert response2.status_code == 200
    assert response2.json()["result"] == "Async: async"
