# SmartPublisher Examples

This directory contains minimal examples to get you started quickly with smartpublisher.

## 🚀 Quick Start Examples

For **complete, production-ready examples**, see the dedicated repository:
**[genropy/smartpublisher-examples](https://github.com/genropy/smartpublisher-examples)**

## Minimal Example (Inline)

The simplest possible smartpublisher app:

```python
from smartswitch import Switcher
from smartpublisher import Publisher

class Calculator:
    """Simple calculator handler."""
    api = Switcher(prefix='calc_')

    @api
    def calc_add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b

    @api
    def calc_multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b

class CalcApp(Publisher):
    def on_init(self):
        self.publish("calc", Calculator())

if __name__ == "__main__":
    app = CalcApp()
    app.run()  # Auto-detects CLI or HTTP mode
```

**Usage**:
```bash
# CLI mode
python calculator.py calc add 5 3
# Output: 8

# HTTP mode (no args = start server)
python calculator.py
# Server starts at http://localhost:8000
# OpenAPI docs at http://localhost:8000/docs
```

## Available Examples in This Directory

This directory contains minimal inline examples. For complete, production-ready examples with full documentation, see the [smartpublisher-examples](https://github.com/genropy/smartpublisher-examples) repository.

## Complete Examples Repository

The **[smartpublisher-examples](https://github.com/genropy/smartpublisher-examples)** repository contains:

- **demo_shop** - Complete e-commerce system with:
  - Database operations with custom DbopPlugin
  - Multiple table managers (articles, purchases, types)
  - SQLite/PostgreSQL adapters
  - Complete test suite
  - Sphinx documentation

- **More examples coming soon**:
  - API Gateway with routing
  - Data Pipeline with validation
  - Microservices architecture
  - Production-ready templates

## Why Separate Repository?

Complex examples:
- Can evolve independently
- Have their own CI/CD
- Don't bloat the main repo
- Are easier to maintain and update

## Contributing Examples

Have a great smartpublisher example? Submit it to:
https://github.com/genropy/smartpublisher-examples

See the repository's CONTRIBUTING.md for guidelines.
