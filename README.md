<div align="center">

<img src="docs/assets/logo.png" alt="smpub Logo" width="200"/>

# smpub - Smart Publisher

**CLI/API framework based on SmartSwitch**

</div>

[![PyPI version](https://img.shields.io/pypi/v/smpub.svg)](https://pypi.org/project/smpub/)
[![Tests](https://github.com/genropy/smpub/actions/workflows/test.yml/badge.svg)](https://github.com/genropy/smpub/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/genropy/smpub/branch/main/graph/badge.svg)](https://codecov.io/gh/genropy/smpub)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation](https://readthedocs.org/projects/smpub/badge/?version=latest)](https://smpub.readthedocs.io/)

---

Build CLI and API applications with automatic command dispatch using [SmartSwitch](https://github.com/genropy/smartswitch).

## Features

- 🎯 **Publisher Pattern** - Register handlers and expose them via CLI/API
- 🔀 **SmartSwitch Integration** - Rule-based function dispatch
- 💻 **CLI Generation** - Automatic command-line interface
- ✅ **Pydantic Validation** - Automatic type validation and conversion
- 🎨 **Interactive Mode** - Optional gum-based parameter prompting
- 🌐 **HTTP/API Mode** - FastAPI with OpenAPI/Swagger UI
- 📝 **Registry System** - Local/global app registration

## Installation

```bash
pip install smpub

# With HTTP support
pip install smpub[http]
```

## Quick Start

### 1. Create a Handler

```python
from smpub import PublishedClass
from smartswitch import Switcher

class UserHandler(PublishedClass):
    __slots__ = ('users',)
    api = Switcher(prefix='user_')

    def __init__(self):
        self.users = {}

    @api
    def user_add(self, name: str, email: str):
        """Add a new user."""
        self.users[name] = email
        return f"User {name} added"

    @api
    def user_list(self):
        """List all users."""
        return list(self.users.keys())
```

### 2. Create an App

```python
from smpub import Publisher
from .handlers import UserHandler

class MainClass(Publisher):
    def initialize(self):
        self.users = UserHandler()
        self.publish('users', self.users, cli=True, openapi=True)

if __name__ == "__main__":
    app = MainClass()
    app.run()  # Auto-detect CLI or HTTP mode
```

### 3. Use It

**CLI Mode:**
```bash
# Register your app
smpub add myapp --path ~/projects/myapp

# Run commands
smpub myapp users add john john@example.com
smpub myapp users list
```

**HTTP Mode:**
```bash
# Start server
python myapp.py
# Opens Swagger UI at http://localhost:8000/docs

# Call API
curl -X POST http://localhost:8000/users/add \
  -H "Content-Type: application/json" \
  -d '{"name": "john", "email": "john@example.com"}'
```

**Interactive Mode:**
```bash
smpub myapp users add --interactive
# Prompts for each parameter with type hints
```

## Documentation

For complete documentation, visit [smpub.readthedocs.io](https://smpub.readthedocs.io).

Topics covered:
- Publisher and handler patterns
- CLI command structure
- Type validation with Pydantic
- Interactive mode with gum
- HTTP/API mode with FastAPI
- Registry system (local/global)
- Architecture and design

## Part of Genro-Libs Family

smpub is part of the [Genro-Libs toolkit](https://github.com/softwell/genro-libs), a collection of general-purpose Python developer tools.

**Related Projects:**
- [smartswitch](https://github.com/genropy/smartswitch) - Rule-based function dispatch (used by smpub)
- [gtext](https://github.com/genropy/gtext) - Text transformation tool

## Requirements

- Python 3.10+
- smartswitch >= 0.1.0
- pydantic >= 2.0
- [gum](https://github.com/charmbracelet/gum) (optional, for interactive mode)

## Development

```bash
git clone https://github.com/genropy/smpub.git
cd smpub
pip install -e ".[dev]"
pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [Documentation](https://smpub.readthedocs.io)
- [GitHub](https://github.com/genropy/smpub)
- [PyPI](https://pypi.org/project/smpub/)
- [Issue Tracker](https://github.com/genropy/smpub/issues)
