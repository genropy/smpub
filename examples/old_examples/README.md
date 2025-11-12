# Old Examples

This directory contains old/incomplete examples that have been superseded by newer, more comprehensive examples.

## Current Examples (Use These!)

See the parent directory for current, maintained examples:

- **sample_shop/** - Complete e-commerce example with SQLite
  - Demonstrates pure Python usage (no smpub required)
  - Includes tests, Jupyter notebook, documentation
  - Shows smartswitch plugin benefits

- **published_shop/** - Optional smpub publisher for sample_shop
  - Shows how to publish an existing Python library
  - Demonstrates separation of library and publisher

## Old Examples (Archive)

The examples in this directory are kept for reference but may be:
- Incomplete
- Using old patterns
- Not tested
- Not documented

**Recommendation**: Use `sample_shop` as the primary example for learning smpub.

## Migration Notes

If you're updating old code, key changes:
1. Classes no longer need `PublishedClass` mixin
2. Use `examples` as a package (has `__init__.py`)
3. Publisher is optional and separate from library code
4. smartswitch plugins (Pydantic, Logging, Smartasync) applied automatically
