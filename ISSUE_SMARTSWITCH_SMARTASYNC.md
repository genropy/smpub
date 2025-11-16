# Feature Request: SmartAsync Integration for Async Method Handling

## Summary

Add native `smartasync` integration to `Switcher` to automatically wrap async methods, making them callable in both sync and async contexts without manual decoration.

## Motivation

When building APIs with async methods, you often need them to work in both sync and async contexts:
- **CLI mode**: Sync context (no event loop)
- **HTTP mode**: Async context (FastAPI/uvicorn)
- **Mixed usage**: Some callers are sync, others are async

**Current workaround**:
```python
from smartasync import smartasync

class MyHandler:
    api = Switcher()

    @api
    @smartasync  # ← Manual decoration required
    async def my_method(self):
        await asyncio.sleep(0.1)
        return "result"
```

**Problem**: Every async method requires manual `@smartasync` decoration.

## Proposed Solution

Add two levels of control for automatic smartasync wrapping:

### 1. Global (Switcher-level)

```python
class MyHandler:
    # Auto-wrap all async methods
    api = Switcher(smartasync=True)

    @api  # ← smartasync applied automatically
    async def my_method(self):
        await asyncio.sleep(0.1)
        return "result"

handler = MyHandler()

# Works in sync context!
callable = handler.api('my_method')
result = callable(handler)  # ✓ No await needed
```

### 2. Per-Call (Method-level)

```python
class MyHandler:
    api = Switcher()  # smartasync=False (default)

    @api
    async def my_method(self):
        return "result"

handler = MyHandler()

# On-demand wrapping
wrapped = handler.api('my_method', smartasync=True)
result = wrapped(handler)  # ✓ Works in sync

# Without wrapping
pure = handler.api('my_method')  # Returns coroutine in sync context
```

## Use Cases

### Use Case 1: CLI with Async Methods
```python
class AppPublisher(Publisher):
    def on_init(self):
        self.db = DatabaseHandler()
        # CLI needs sync calls, but methods are async
        self.publish('db', self.db)

class DatabaseHandler:
    api = Switcher(smartasync=True)  # ← Auto-wrap for CLI

    @api
    async def get_user(self, user_id: int):
        """Async database query"""
        async with aiohttp.ClientSession() as session:
            return await session.get(f"/users/{user_id}")

# CLI usage (sync context)
$ smpub db get_user --user_id 123  # ✓ Works!
```

### Use Case 2: Mixed Sync/Async API
```python
class MixedHandler:
    api = Switcher()

    @api
    def sync_method(self):
        return "sync"

    @api
    async def async_method(self):
        await asyncio.sleep(0.1)
        return "async"

handler = MixedHandler()

# Choose wrapping per method
sync_call = handler.api('sync_method')  # No wrapping needed
async_call = handler.api('async_method', smartasync=True)  # Wrap for sync context
```

### Use Case 3: HTTP + CLI Dual Mode
```python
class DualModeHandler:
    api = Switcher(smartasync=True)  # Auto-wrap for flexibility

    @api
    async def fetch_data(self, url: str):
        """Works in both CLI and HTTP"""
        async with httpx.AsyncClient() as client:
            return await client.get(url)

# CLI (sync)
$ smpub app fetch_data --url "https://api.example.com"

# HTTP (async)
# FastAPI automatically handles with await
```

## Implementation

### Changes to `Switcher.__init__()`

```python
class Switcher:
    def __init__(
        self,
        name: str | None = None,
        prefix: str | None = None,
        parent: "Switcher | None" = None,
        wrap_methods: bool = True,
        smartasync: bool = False,  # ← NEW: auto-wrap async methods
    ):
        self._name = name
        self._prefix = prefix
        self._parent = parent
        self._wrap_methods = wrap_methods
        self._smartasync = smartasync  # ← Store flag
        # ... rest of init
```

### Changes to `__call__()`

```python
def __call__(self, key: str, smartasync: bool | None = None) -> Callable:
    """
    Get a callable for the given method.

    Args:
        key: Method name
        smartasync: Override Switcher-level smartasync setting.
                   True = wrap with smartasync
                   False = don't wrap
                   None = use Switcher setting (default)
    """
    entry = self._methods[key]

    # Determine if we should wrap with smartasync
    should_wrap_async = smartasync if smartasync is not None else self._smartasync

    if should_wrap_async:
        # Wrap the callable with smartasync
        return self._create_smartasync_wrapper(entry)
    else:
        # Normal behavior
        return _SwitchCall(self, entry)
```

### Helper Method

```python
def _create_smartasync_wrapper(self, entry):
    """Create a smartasync-wrapped callable for the entry."""
    try:
        from smartasync import smartasync
    except ImportError:
        raise ImportError(
            "smartasync is required for smartasync=True. "
            "Install with: pip install smartasync"
        )

    # Get the normal callable
    switch_call = _SwitchCall(self, entry)

    # Wrap it with smartasync if the function is async
    if asyncio.iscoroutinefunction(entry.func):
        # Create a wrapper that smartasync can wrap
        def wrapper(*args, **kwargs):
            return switch_call(*args, **kwargs)

        # Apply smartasync decorator
        wrapped = smartasync(wrapper)
        return wrapped
    else:
        # Not async, return as-is
        return switch_call
```

## Benefits

### 1. Cleaner Code
```python
# Before (manual decoration)
@api
@smartasync
async def method(self): pass

# After (automatic)
api = Switcher(smartasync=True)

@api
async def method(self): pass
```

### 2. Flexibility
```python
# Different strategies per Switcher
public_api = Switcher(smartasync=True)   # Always sync-callable
internal = Switcher(smartasync=False)     # Raw async (performance)
```

### 3. On-Demand Control
```python
# Same method, different contexts
cli_call = api('method', smartasync=True)    # For CLI
http_call = api('method', smartasync=False)  # For FastAPI
```

## Dependency

This feature requires `smartasync` package:
- Make it an **optional dependency** in `pyproject.toml`
- Only import when `smartasync=True` is used
- Raise clear error if not installed

```toml
[project.optional-dependencies]
async = ["smartasync>=0.5.0"]
```

## Edge Cases

### Non-async methods with smartasync=True
```python
@api
def sync_method(self): pass

# smartasync is a no-op for sync methods
callable = api('sync_method', smartasync=True)  # No wrapping, works fine
```

### Already-wrapped methods
```python
@api
@smartasync  # Manual decoration
async def method(self): pass

# Double-wrapping detection
callable = api('method', smartasync=True)
# Should detect existing wrapping and not double-wrap
```

## Backward Compatibility

✅ **Fully backward compatible**
- Default `smartasync=False` maintains current behavior
- No changes to existing code required
- Opt-in feature

## Testing

Required tests:
1. `test_smartasync_switcher_level()` - global auto-wrapping
2. `test_smartasync_call_level()` - per-call wrapping
3. `test_smartasync_override()` - call-level overrides switcher-level
4. `test_smartasync_sync_method()` - no-op for sync methods
5. `test_smartasync_missing_dependency()` - error if smartasync not installed
6. `test_smartasync_async_context()` - works in async context
7. `test_smartasync_sync_context()` - works in sync context

## Documentation

Update:
- `README.md` - add async handling section
- `docs/guide/async.md` - new guide for async patterns
- `docs/guide/plugins.md` - explain smartasync integration
- API reference - document `smartasync` parameter

## Related Issues

- #24 - Optional Method Wrapping (`wrap_methods` parameter)
  - This feature complements `wrap_methods`
  - Both can be used together

## Priority

**Medium-High** - Important for frameworks that need dual sync/async support (CLI + HTTP).

## Implementation Effort

**Medium** - Requires smartasync integration, careful handling of async/sync contexts, testing both modes.

---

**Labels**: `enhancement`, `feature-request`, `async`, `api`
**Milestone**: v0.4.0 or v0.5.0
