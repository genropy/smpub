# Plugin Configuration Enhancement Proposal

**Status**: ✅ IMPLEMENTED in smartswitch v0.10.0 (commit e531174)
- **Issue**: [smartswitch #22](https://github.com/genropy/smartswitch/issues/22) (closed)
- **Implementation**: See [Implemented API](#implemented-api) section below

---

## Implemented API

The feature has been implemented with the following API (slightly improved from original proposal):

### Basic Usage with Flags

```python
api = Switcher()
api.plug('logging', flags='print,enabled,time')
```

**Available flags:**
- `enabled` - Enable plugin (default: False, opt-in)
- `print` - Use print() for output
- `log` - Use Python logging (default: True)
- `before` - Show input parameters (default: True)
- `after` - Show return value (default: False)
- `time` - Show execution time (default: False)

### Per-Method Configuration

```python
api.plug('logging',
    flags='print,enabled,after',  # Global configuration
    method_config={
        'method1': 'enabled:off',           # Disable for specific method
        'method2,method3': 'after,time',    # Override for multiple methods
    }
)
```

**Key features:**
- `method_config` dict maps method names (or comma-separated lists) to flag strings
- Methods not in `method_config` inherit global `flags`
- Use `:off` suffix to disable a flag (e.g., `enabled:off`, `before:off`)
- Default is `enabled=False` - plugin must be explicitly enabled

### Runtime Configuration

```python
# Get plugin reference
logger = api.plugin('logging')

# Update global flags at runtime
logger.configure.flags = 'log,enabled,time'

# Update specific method flags
logger.configure['calculate'].flags = 'enabled:off'
```

---

## Original Proposal (Historical)

Below is the original proposal for reference. The actual implementation uses a slightly different API as shown above.

## Current Status (at proposal time)

Currently, LoggingPlugin configuration works with mode strings:

```python
class Repository:
    api = Switcher()
    api.plug('logging', mode='print,time')

    @api
    def branches(self): ...

    @api
    def history(self, limit=10): ...
```

**Limitations**:
- All methods get the same configuration
- To disable plugin for specific methods, must use runtime control:
  ```python
  Repository.api.set_plugin_enabled(repo, "history", "logging", enabled=False)
  ```
- Cannot set initial enabled/disabled state at plugin registration time

## Proposed Enhancement

### 1. Mode String with enabled/disabled Flag

Support initial enabled/disabled state in mode string:

```python
# Start with plugin disabled by default
api.plug('logging', mode='disabled,print,time')

# Explicitly enable (default behavior)
api.plug('logging', mode='enabled,print,time')
```

**Semantics**:
- `enabled` (or omitted): Plugin is active for all methods by default
- `disabled`: Plugin is inactive for all methods by default
- Can still be controlled at runtime with `set_plugin_enabled()`

### 2. Dict-based Granular Configuration

Support per-method configuration using dictionary:

```python
api.plug('logging', config={
    '*': 'enabled,print',              # Default for all methods
    'history': 'disabled',             # Disable for history
    'info': 'enabled,log,time',        # Use logging with timing for info
    'branches,tags': 'enabled,print'   # Same config for multiple methods
})
```

**Semantics**:
- `'*'`: Default configuration for all methods
- Single method name: `'history'`
- Multiple methods (comma-separated): `'branches,tags'`
- Each value is a mode string (with enabled/disabled flag)

### 3. Mixed Mode (mode + config)

When both `mode` and `config` are provided:

```python
api.plug('logging',
    mode='disabled,print',  # Global default
    config={
        'info': 'enabled,log,time'  # Override for specific method
    }
)
```

**Semantics**:
- `mode` sets the global default
- `config` entries override for specific methods

## Implementation Requirements

### A. LoggingPlugin Changes

The LoggingPlugin needs to:

1. **Parse enabled/disabled in mode string**:
   ```python
   def __init__(self, mode='print', config=None, **kwargs):
       flags = set(f.strip() for f in mode.split(','))
       self.initially_enabled = 'disabled' not in flags
       # ... existing flag parsing
   ```

2. **Store per-method configurations**:
   ```python
   self.method_configs = {}  # method_name -> mode_flags dict
   if config:
       self._parse_config_dict(config)
   ```

3. **Apply configuration during decoration or at call time**:
   - Option A: Set activation state during `on_decorate()`
   - Option B: Check at call time in `wrap_handler()`

### B. Switcher Core Changes

Minimal changes needed - the logic can be in LoggingPlugin:

1. **Pass config parameter through**:
   - `.plug()` already accepts `**config`
   - LoggingPlugin `__init__` receives it

2. **Plugin can use Switcher.set_plugin_enabled() during on_decorate()**:
   ```python
   def on_decorate(self, switch, func, entry):
       # Apply per-method configuration
       method_name = entry.name
       if method_name in self.method_configs:
           mode = self.method_configs[method_name]
           enabled = 'disabled' not in mode
           # Store initial state - will be checked at runtime
   ```

### C. Activation Timing

The plugin wrapper chain is built once during decoration, but includes runtime checks via `is_plugin_enabled()`. Therefore:

- **Initial state** can be set during `on_decorate()` using `set_plugin_enabled()`
- **Runtime changes** continue to work as before
- **No need** to rebuild wrapper chain

## Usage Examples

### Example 1: Start Disabled, Enable Selectively

```python
class Repository:
    api = Switcher()
    api.plug('logging', config={
        '*': 'disabled',              # Disabled by default
        'info': 'enabled,print,time'  # Enable only for info
    })
```

Output:
```
# repo.branches() -> no output (disabled)
# repo.history() -> no output (disabled)
# repo.info() ->
→ info()
← info() -> {...} (0.0001s)
```

### Example 2: Different Modes per Method

```python
class Repository:
    api = Switcher()
    api.plug('logging', config={
        '*': 'enabled,print',                # Print by default
        'history,tags': 'enabled,log,time',  # Use logging with timing
        'internal_method': 'disabled'        # Disable completely
    })
```

### Example 3: Global + Specific Overrides

```python
class Repository:
    api = Switcher()
    api.plug('logging',
        mode='enabled,print',  # Global default
        config={
            'debug_info': 'disabled'  # Turn off for debug method
        }
    )
```

## Benefits

1. **Declarative Configuration**: Set up everything at plugin registration
2. **No Boilerplate**: No need for manual `set_plugin_enabled()` calls
3. **Clear Intent**: Configuration is visible where Switcher is defined
4. **Backward Compatible**: Existing code continues to work
5. **Flexible**: Can still use runtime control to override

## Testing Strategy

Create test cases for:

1. Mode string with 'disabled' flag
2. Dict config with wildcard '*'
3. Dict config with single method
4. Dict config with comma-separated methods
5. Mixed mode + config
6. Runtime override of initial config
7. Per-instance isolation (ensure config doesn't leak between instances)

## Next Steps

1. **Validate Proposal**: Review with smartswitch maintainer
2. **Create Issue**: Document in smartswitch GitHub issues
3. **Implement in LoggingPlugin**: Add config dict parsing
4. **Test Thoroughly**: Use gitsample examples as test bed
5. **Document**: Update LoggingPlugin docstring
6. **Consider for Other Plugins**: Pattern could apply to other plugins

## Open Questions

1. Should `config` parameter name clash with BasePlugin's `config` dict?
   - Maybe use `method_modes` or `per_method` instead?

2. Should we support regex patterns for method names?
   ```python
   config={
       'get_*': 'enabled,print',
       'set_*': 'enabled,log'
   }
   ```

3. Should initial state be stored per-instance or globally?
   - Probably globally (class-level) since it's set at decoration time
   - Runtime changes are per-instance (as currently)
