# Feature Request: Optional Method Wrapping in Switcher

## Summary

Add a `wrap_methods` parameter to `Switcher` to control whether decorated methods are wrapped for direct (pythonic) calls, while still applying plugins when called via the switcher dispatcher.

## Motivation

Currently, when you decorate a method with `@switcher`, the decorator **always** wraps the original method, applying plugins for both:
- Direct pythonic calls: `obj.method()`
- Switcher dispatcher calls: `switcher('method')(obj)`

This behavior is great for consistency, but there are scenarios where you want:
- **Direct calls** → Pure function (no plugin overhead)
- **Dispatcher calls** → Full plugin chain (validation, logging, etc.)

**Use cases**:
1. **Internal methods**: Used frequently in internal code paths where validation is redundant
2. **Performance-critical paths**: Direct calls skip plugin overhead
3. **Hybrid APIs**: Public methods always validated, internal methods validated only at boundaries
4. **Testing**: Access to pure functions for unit testing

## Proposed Solution

Add a `wrap_methods` parameter to `Switcher.__init__()`:

```python
class MyHandler:
    # Default behavior (current): wraps methods
    api = Switcher(name="api").plug("pydantic")

    # New behavior: registers but doesn't wrap
    internal = Switcher(name="internal", wrap_methods=False).plug("pydantic")

    @api
    def public_method(self, x: int):
        """Always validated (both pythonic and dispatcher calls)"""
        return x * 2

    @internal
    def internal_method(self, x: int):
        """Validated only via dispatcher"""
        return x * 3

handler = MyHandler()

# Public method - always validated
handler.public_method("wrong")  # ✗ ValidationError
handler.api('public_method')(handler, "wrong")  # ✗ ValidationError

# Internal method - validated only via dispatcher
handler.internal_method("wrong")  # ✓ OK (pure function, no wrapping)
handler.internal('internal_method')(handler, "wrong")  # ✗ ValidationError
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
        wrap_methods: bool = True,  # ← NEW parameter
    ):
        self._name = name
        self._prefix = prefix
        self._parent = parent
        self._wrap_methods = wrap_methods  # ← Store flag
        # ... rest of init
```

### Changes to `_decorate()`

```python
def _decorate(self, func: Callable) -> Callable:
    """Decorate and register a function."""
    # Always register in switcher
    entry = self._register_method(func)

    # Wrap only if wrap_methods=True (default)
    if self._wrap_methods:
        # Current behavior: create wrapper with plugin chain
        return self._create_wrapper(func, entry)
    else:
        # New behavior: return original function (no wrapping)
        # Plugins will still be applied when called via dispatcher
        return func
```

### Key Points

1. **Registration always happens** - method is always registered in `_methods` dict
2. **Wrapping is conditional** - if `wrap_methods=False`, decorator returns original function
3. **Dispatcher always applies plugins** - calling via `switcher(name)` always goes through plugin chain
4. **Backward compatible** - default `wrap_methods=True` maintains current behavior

## Benefits

### 1. Performance
```python
# Hot path - no plugin overhead
for item in large_list:
    result = handler.process_item(item)  # Direct call, no wrapping

# Validation at boundaries only
validated_items = handler.api('process_items')(handler, user_input)
```

### 2. Clear Intent
```python
class DataProcessor:
    # Public API - always validated
    api = Switcher(name="api").plug("pydantic")

    # Internal utilities - fast paths
    utils = Switcher(name="utils", wrap_methods=False)

    @api
    def process(self, data: dict):
        """Public API - validated"""
        # Internal calls are fast
        return self._transform(data)

    @utils
    def _transform(self, data):
        """Internal - no overhead"""
        return data
```

### 3. Flexible Architecture
```python
class AppHandler:
    # Different validation strategies per logical group
    public = Switcher(wrap_methods=True).plug("pydantic")
    internal = Switcher(wrap_methods=False).plug("pydantic")
    debug = Switcher(wrap_methods=True).plug("logging", mode="verbose")
```

## Pattern: Multi-Switcher Architecture

This feature enables a powerful pattern:

```python
class ComplexHandler:
    # Public API - strict validation, logging
    api = Switcher(name="api").plug("pydantic").plug("logging")

    # Internal methods - validated at boundaries
    internal = Switcher(name="internal", wrap_methods=False).plug("pydantic")

    # Pure utilities - no plugins
    utils = Switcher(name="utils", wrap_methods=False)

    @api
    def create_user(self, email: str, age: int):
        """Public API endpoint"""
        # Validate at boundary
        normalized = self.internal('normalize_email')(self, email)
        # Fast internal calls
        return self._save_to_db(normalized, age)

    @internal
    def normalize_email(self, email: str):
        """Can be validated via dispatcher when needed"""
        return email.lower().strip()

    @utils
    def _save_to_db(self, email, age):
        """Pure function, no overhead"""
        # ... database logic
```

## Alternatives Considered

### Alternative 1: Per-method flag `@switcher(weak=True)`
```python
@switcher(weak=True)
def my_method(self): pass
```

**Pros**: Maximum granularity
**Cons**: More complex, requires metadata per entry, less clear grouping

### Alternative 2: Plugin enable/disable flags
```python
switcher = Switcher().plug("pydantic", enabled=False)
```

**Pros**: Runtime control
**Cons**: Still has wrapping overhead, less explicit

**Decision**: Per-Switcher flag is the sweet spot - clear, simple, flexible with multi-switcher pattern.

## Backward Compatibility

✅ **Fully backward compatible**
- Default `wrap_methods=True` maintains current behavior
- No changes required to existing code
- Opt-in feature

## Testing

Required tests:
1. `test_wrap_methods_true_default()` - verify default behavior unchanged
2. `test_wrap_methods_false_no_wrapping()` - verify direct calls don't apply plugins
3. `test_wrap_methods_false_dispatcher_applies_plugins()` - verify dispatcher still works
4. `test_multiple_switchers_different_wrapping()` - verify multi-switcher pattern
5. `test_wrap_methods_with_various_plugins()` - test with pydantic, logging, custom plugins

## Documentation

Update:
- `README.md` - add section on method wrapping control
- `docs/guide/plugins.md` - explain wrapping behavior
- `docs/guide/best-practices.md` - multi-switcher pattern examples
- API reference - document `wrap_methods` parameter

## Priority

**Medium** - Nice to have for performance optimization and architectural flexibility, but current behavior is acceptable for most use cases.

## Implementation Effort

**Low-Medium** - Straightforward change to decorator logic, main effort is testing and documentation.

---

**Related Issues**: None
**Related PRs**: None
**Labels**: `enhancement`, `feature-request`, `api`
