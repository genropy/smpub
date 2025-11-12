# smpub Examples

This directory contains examples demonstrating smpub usage.

## 🎯 Primary Example: sample_shop

**Start here!** The `sample_shop` example is a complete, well-documented e-commerce application.

### Features

- ✅ **Standalone Python library** - works without smpub
- ✅ **Comprehensive tests** - 10/10 passing
- ✅ **Interactive Jupyter notebook** - explore interactively
- ✅ **Complete documentation** - README + plugin explanation
- ✅ **Real-world patterns** - SQLite backend, proper structure
- ✅ **smartswitch benefits** - see how plugins reduce boilerplate

### Quick Start

```bash
# 1. Pure Python usage (no smpub)
cd examples
python -m sample_shop.example_pythonic

# 2. Interactive exploration
jupyter notebook sample_shop/shop_usage.ipynb

# 3. Run tests
pytest sample_shop/test_shop.py -v

# 4. Optional: CLI/HTTP publishing
cd published_shop
python main.py types list              # CLI
python main.py --mode http             # HTTP server
```

### What You'll Learn

1. **How to write classes that use smartswitch**
   - Normal Python classes with type hints
   - Automatic validation via PydanticPlugin
   - No manual validation boilerplate

2. **How smartswitch plugins reduce code**
   - See `PLUGINS_EXPLANATION.md`
   - Compare before/after examples
   - ~10 lines of validation → 0 lines!

3. **How to optionally publish with smpub**
   - See `published_shop/main.py`
   - Just import and publish - that's it!
   - Library doesn't know about smpub

## 📁 Structure

```
examples/
├── README.md                # This file
├── __init__.py              # Package marker
│
├── PLUGINS_EXPLANATION.md   # How plugins reduce boilerplate (shared)
│
├── sample_shop/             # ⭐ PRIMARY EXAMPLE
│   ├── tables/              # Database table managers
│   ├── shop.py              # Main Shop class
│   ├── example_pythonic.py  # Pure Python usage demo
│   ├── shop_usage.ipynb     # Interactive Jupyter notebook
│   ├── test_shop.py         # Comprehensive tests (10/10 ✅)
│   └── README.md            # Detailed documentation
│
├── published_shop/          # Publisher for sample_shop
│   ├── main.py              # Minimal publisher (imports Shop)
│   └── README.md            # Publishing examples
│
└── old_examples/            # Archive of old/incomplete examples
    └── README.md            # Migration notes
```

## 📚 Documentation

- **PLUGINS_EXPLANATION.md** - How plugins work and save code (shared)
- **sample_shop/README.md** - Complete usage guide
- **sample_shop/shop_usage.ipynb** - Interactive learning
- **published_shop/README.md** - Publishing patterns

## 🧪 Testing

All examples are tested:

```bash
# Run sample_shop tests
pytest examples/sample_shop/test_shop.py -v
# Result: 10 passed ✅
```

## 💡 Key Concepts Demonstrated

### 1. Library First, Publisher Optional

```
sample_shop/        ← Standalone Python library (no smpub)
  ├── shop.py       ← Works on its own
  └── ...

published_shop/    ← OPTIONAL publisher (separate!)
  └── main.py       ← Just imports and publishes
```

### 2. Normal Python Classes

```python
class Articles:
    """Normal Python class - no smpub awareness!"""

    def add(
        self,
        code: str,
        price: Annotated[float, Field(gt=0)]  # ← Automatic validation!
    ) -> dict:
        # Business logic directly - no validation boilerplate
        with get_connection() as conn:
            # ... actual work
```

### 3. Plugin Benefits

Without plugins (manual):
```python
def add(self, price):
    if not isinstance(price, (int, float)):
        return {"error": "price must be number"}
    if price <= 0:
        return {"error": "price must be > 0"}
    # ... finally, business logic
```

With plugins (automatic):
```python
def add(self, price: Annotated[float, Field(gt=0)]):
    # Business logic directly!
```

**Savings**: ~10 lines per method × many methods = hundreds of lines!

## 🚀 Next Steps

1. **Understand the plugin benefits**
   - Read `PLUGINS_EXPLANATION.md` (start here!)
   - See how plugins eliminate boilerplate

2. **Explore sample_shop**
   - Read `sample_shop/README.md`
   - Run `example_pythonic.py`
   - Open the Jupyter notebook

3. **See publishing in action**
   - Check `published_shop/main.py`
   - See how simple it is (just import + publish)

4. **Study the patterns**
   - Compare code with/without plugins
   - See test coverage
   - Explore real-world patterns

## 📞 Questions?

- Check `PLUGINS_EXPLANATION.md` for detailed plugin explanations
- Review tests in `sample_shop/test_shop.py` for usage patterns
- Explore the Jupyter notebook for interactive learning
