---
name: Add Async Handler Support
about: Implement async/await support for HTTP API handlers
title: 'feat: Add async handler support for HTTP endpoints'
labels: enhancement, priority-high
assignees: ''
---

## Problem

Currently, async methods are NOT properly awaited in HTTP endpoints. The endpoint is `async def`, but the handler call is missing `await`:

```python
# Current code (WRONG)
async def endpoint_func(body: model_cls):
    result = method_ref(**params_dict)  # ❌ No await!
    return {"result": result}
```

This breaks async handlers like:
```python
class DataHandler(PublishedClass):
    api = ApiSwitcher(prefix='data_')

    @api
    async def fetch_from_api(self, endpoint: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint)  # This never runs!
            return response.json()
```

## Solution

Check if the method is a coroutine and await it:

```python
import inspect

async def endpoint_func(body: model_cls):
    params_dict = body.model_dump()

    # Check if method is async
    if inspect.iscoroutinefunction(method_ref):
        result = await method_ref(**params_dict)  # ✅ Await async
    else:
        result = method_ref(**params_dict)  # ✅ Call sync

    return {"result": result}
```

## Implementation Checklist

### 1. Code Changes

- [ ] Add `import inspect` to `src/smpub/api_server.py`
- [ ] Modify `make_endpoint()` function (line ~131):
  - [ ] Check `inspect.iscoroutinefunction(method_ref)`
  - [ ] Use `await` for async methods
- [ ] Modify `make_simple_endpoint()` function (line ~160):
  - [ ] Check `inspect.iscoroutinefunction(method_ref)`
  - [ ] Use `await` for async methods

### 2. Tests

- [ ] Create `tests/test_async_handlers.py`:
  - [ ] Test async method via HTTP API
  - [ ] Test sync method still works
  - [ ] Test mixed async/sync handlers in same app
  - [ ] Test async method that raises exception
  - [ ] Test async method with no parameters

Example test:
```python
import asyncio
import pytest
from httpx import AsyncClient
from smartpublisher import Publisher, PublishedClass
from smartpublisher.apiswitcher import ApiSwitcher
from smartpublisher.api_server import create_fastapi_app

class AsyncHandler(PublishedClass):
    api = ApiSwitcher(prefix='async_')

    @api
    async def fetch_data(self, url: str) -> dict:
        """Async method example."""
        await asyncio.sleep(0.1)  # Simulate async I/O
        return {"url": url, "status": "fetched"}

    @api
    def process_sync(self, data: str) -> str:
        """Sync method example."""
        return data.upper()

class AsyncApp(Publisher):
    def initialize(self):
        self.publish(AsyncHandler(), cli=True, openapi=True)

@pytest.mark.asyncio
async def test_async_handler_http():
    """Test async handler via HTTP API."""
    app = AsyncApp()
    fastapi_app = create_fastapi_app(app)

    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        response = await client.post(
            "/async/fetch_data",
            json={"url": "https://example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"]["status"] == "fetched"

@pytest.mark.asyncio
async def test_sync_handler_still_works():
    """Test sync handler still works after async support."""
    app = AsyncApp()
    fastapi_app = create_fastapi_app(app)

    async with AsyncClient(app=fastapi_app, base_url="http://test") as client:
        response = await client.post(
            "/async/process_sync",
            json={"data": "hello"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["result"] == "HELLO"
```

### 3. Documentation

- [ ] Update `WHY_SMPUB.md`:
  - [ ] Remove "Async handlers not supported" from cons
  - [ ] Add async example to pros section
- [ ] Update `docs/appendix/architecture.md`:
  - [ ] Add async support note to HTTP Layer section
  - [ ] Add async example
- [ ] Create `examples/async_app/main.py`:
  - [ ] Example with async HTTP calls
  - [ ] Example with async database queries
  - [ ] Example mixing sync and async methods

### 4. Example Code

Add to docs:
```python
from smartpublisher import Publisher, PublishedClass
from smartpublisher.apiswitcher import ApiSwitcher
import httpx
import asyncio

class AsyncDataHandler(PublishedClass):
    api = ApiSwitcher(prefix='data_')

    @api
    async def fetch_from_api(self, endpoint: str) -> dict:
        """Fetch data from external API (async I/O)."""
        async with httpx.AsyncClient() as client:
            response = await client.get(endpoint)
            return response.json()

    @api
    async def process_batch(self, urls: list[str]) -> list[dict]:
        """Process multiple URLs concurrently."""
        tasks = [self.fetch_from_api(url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

    @api
    def process_local(self, data: str) -> str:
        """Process data locally (sync CPU-bound)."""
        return data.upper()

class AsyncApp(Publisher):
    def initialize(self):
        self.publish(AsyncDataHandler(), cli=True, openapi=True)

if __name__ == "__main__":
    app = AsyncApp()
    app.run()
```

Usage:
```bash
# Start server
smpub asyncapp serve

# Call async endpoint
curl -X POST http://localhost:8000/data/fetch_from_api \
  -H "Content-Type: application/json" \
  -d '{"endpoint": "https://api.example.com/data"}'

# Call sync endpoint (still works)
curl -X POST http://localhost:8000/data/process_local \
  -H "Content-Type: application/json" \
  -d '{"data": "hello"}'
```

## Benefits

✅ **Real-world async I/O**: Database queries, HTTP calls, file I/O
✅ **Concurrent requests**: Better performance for I/O-bound operations
✅ **Mixed sync/async**: Use async only where needed
✅ **No breaking changes**: Existing sync handlers continue to work

## Estimated Effort

**2-3 hours** total:
- Implementation: 30 minutes
- Tests: 1 hour
- Documentation: 1 hour
- Examples: 30 minutes

## Priority

🔥 **HIGH** - Essential for real-world API integrations

## Related Issues

None

## References

- FastAPI async support: https://fastapi.tiangolo.com/async/
- Python asyncio: https://docs.python.org/3/library/asyncio.html
