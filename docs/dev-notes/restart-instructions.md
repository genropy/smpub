# 🔄 RESTART INSTRUCTIONS - smpub

**Created**: 2025-11-09
**Status**: Core structure created, needs implementation
**Branch**: Not yet initialized as git repo

---

## ⚡ Quick Start

1. **Verifica struttura progetto**:
   ```bash
   cd /Users/gporcari/Sviluppo/genro_ng/meta-genro-libs/sub-projects/smpub
   ls -la src/smpub/
   # Dovresti vedere: __init__.py, cli.py, publisher.py, published.py
   ```

2. **Installa in development mode**:
   ```bash
   pip install -e .
   # Ora il comando 'smpub' sarà disponibile
   ```

3. **Testa con sample app**:
   ```bash
   cd examples/sample_app
   python sample_app.py --help
   ```

---

## 🎯 Obiettivo del Progetto

**smpub** (Smart Publisher) è un framework CLI/API basato su SmartSwitch per costruire applicazioni command-line e web con dispatch automatico.

**Pattern architetturale**:
```
Publisher (your app)
  ├─ parent_api: Switcher          # Root API registry
  └─ published_instances
      └─ 'users' → UserHandler
          └─ api: Switcher          # Handler API (class var)
              ├─ user_add           # Methods
              ├─ user_list
              └─ ...
```

---

## 📋 Stato Attuale

### ✅ Implementato

**Core Classes**:
- [x] `PublishedClass` mixin in `src/smpub/published.py`
- [x] `Publisher` base class in `src/smpub/publisher.py`
- [x] CLI entry point in `src/smpub/cli.py`
- [x] Package exports in `src/smpub/__init__.py`

**Registry System**:
- [x] Locale (`./.published`)
- [x] Globale (`~/.smartlibs/publisher/registry.json`)
- [x] Comandi: `add`, `remove`, `list`

**Documentazione**:
- [x] README.md completo
- [x] CLAUDE.md per sviluppo
- [x] LICENSE (MIT)
- [x] pyproject.toml

**Esempi**:
- [x] `examples/publisher/` - Publisher base (legacy da temp)
- [x] `examples/sample_app/` - App multi-handler (da aggiornare)

### ❌ Da Implementare

**Publisher Methods** (`src/smpub/publisher.py`):
- [ ] `_run_cli()` - Parse argv e dispatch a handlers
  - Parse: `smpub myapp handler method args`
  - Generate help automatico da docstrings
  - Dispatch usando SmartSwitch
- [ ] `_run_http()` - FastAPI server con auto-routing
  - Create FastAPI app
  - Generate routes da handlers
  - OpenAPI spec generation

**Testing**:
- [ ] `tests/test_published.py` - PublishedClass tests
- [ ] `tests/test_publisher.py` - Publisher tests
- [ ] `tests/test_cli.py` - CLI registry tests
- [ ] `tests/test_integration.py` - End-to-end tests

**Sample App**:
- [ ] Aggiornare handlers per usare `PublishedClass`
- [ ] Aggiungere esempi più complessi
- [ ] README per sample app

**Documentation**:
- [ ] `docs/quickstart.md`
- [ ] `docs/guide/handlers.md`
- [ ] `docs/guide/cli.md`
- [ ] `docs/api/publisher.md`

---

## 🗂️ Struttura Progetto

```
smpub/
├── src/smpub/
│   ├── __init__.py          # ✅ Exports: Publisher, PublishedClass
│   ├── cli.py               # ✅ CLI entry point + registry
│   ├── publisher.py         # ⚠️  Publisher class (run methods TODO)
│   └── published.py         # ✅ PublishedClass mixin
│
├── examples/
│   ├── publisher/           # Legacy publisher code
│   │   └── publisher.py
│   └── sample_app/          # Multi-handler example
│       ├── sample_app.py    # ⚠️  Updated to use smpub
│       └── classes/
│           ├── L1_alpha.py  # ❌ Needs PublishedClass
│           ├── L1_beta.py   # ❌ Needs PublishedClass
│           └── L1_gamma.py  # ❌ Needs PublishedClass
│
├── tests/                   # ❌ To be created
├── docs/                    # ❌ To be created
│
├── pyproject.toml          # ✅ Complete
├── README.md               # ✅ Complete
├── CLAUDE.md               # ✅ Development guide
├── LICENSE                 # ✅ MIT
└── RESTART.md              # ✅ This file
```

---

## 🔨 Priorità di Lavoro

### Priority 1: CLI Mode Implementation

**File**: `src/smpub/publisher.py` → `_run_cli()`

**Requirements**:
1. Parse `sys.argv` → `handler_name`, `method_name`, `args`
2. Lookup handler in `self._cli_handlers`
3. Get handler's Switcher (class var `api`)
4. Check if method exists in `api.entries()`
5. Extract signature from handler method
6. Parse args according to signature
7. Call method via Switcher
8. Handle errors gracefully

**Example Flow**:
```bash
$ smpub myapp users add john john@example.com
                  ↓     ↓   ↓
            handler  method args
```

### Priority 2: Update Sample App

**Files**: `examples/sample_app/classes/*.py`

**Changes needed**:
```python
# Before
class L1_alpha:
    api = Switcher(prefix='alpha_')

# After
from smartpublisher import PublishedClass

class L1_alpha(PublishedClass):
    __slots__ = ('registry',)
    api = Switcher(prefix='alpha_')
```

### Priority 3: Testing

Create comprehensive test suite.

---

## 🎓 Key Design Decisions

1. **PublishedClass with __slots__**:
   - Provides `parent_api` slot
   - Subclasses add their own slots
   - No `__dict__` bloat

2. **Registry Files**:
   - Local: `./.published` (JSON)
   - Global: `~/.smartlibs/publisher/registry.json`
   - Human-readable format

3. **Convention over Configuration**:
   - Apps expected to have `main.py` with `MainClass`
   - Handlers have `api = Switcher()` class variable

4. **Exposure Control**:
   - `publish(name, obj, cli=True, openapi=True)`
   - Fine-grained control per handler

5. **Auto-detect Mode**:
   - CLI if `sys.argv` has args
   - HTTP otherwise

---

## 🔍 Dependencies

**Runtime**:
- `smartswitch>=0.1.0` (from genropy/smartswitch)

**Development**:
- `pytest>=7.0`
- `pytest-cov>=4.0`
- `black>=23.0`
- `ruff>=0.1.0`
- `mypy>=1.0`

**Future (for HTTP mode)**:
- `fastapi>=0.100` (when implementing `_run_http`)
- `uvicorn>=0.23` (ASGI server)

---

## 🧪 Testing Strategy

### Unit Tests
- `PublishedClass` slot behavior
- `Publisher.__init__` and initialize hook
- `publish()` injection logic
- CLI registry operations (add/remove/list/load)

### Integration Tests
- Complete app lifecycle
- CLI command execution
- Registry persistence
- Error handling

### Examples as Tests
- Sample app should be runnable
- Use as integration test fixture

---

## 📌 Common Commands

```bash
# Development
pip install -e ".[dev]"

# Testing
pytest -v --cov=src/smpub

# Linting
black src/ tests/
ruff check src/ tests/
mypy src/

# CLI testing
smpub --help
smpub list
smpub add testapp --path examples/sample_app
smpub testapp --help

# Sample app
cd examples/sample_app
python sample_app.py --help
```

---

## ⚠️ Important Notes

1. **Not a Git Repo Yet**: Initialize when ready:
   ```bash
   git init
   git remote add origin git@github.com:genropy/smartpublisher.git
   ```

2. **Part of Genro-Libs**:
   - Coordinate with meta-genro-libs
   - Follow Genro-Libs standards
   - Update ORGANIZATION.md when publishing

3. **SmartSwitch Integration**:
   - Depends on smartswitch
   - Uses Switcher for dispatch
   - Leverages parent/child hierarchy

4. **Language Policy**:
   - Code/docs: English
   - Commit messages: English
   - Communication: Italian (user preference)

---

## 🚀 Next Steps for New Session

1. **Implement `_run_cli()`**:
   - Start with basic arg parsing
   - Add help generation
   - Test with sample app

2. **Update Sample App**:
   - Add `PublishedClass` to all handlers
   - Test `publish()` injection
   - Verify parent_api linkage

3. **Write Tests**:
   - Start with unit tests
   - Add integration tests
   - Use sample app as fixture

4. **Documentation**:
   - API reference
   - User guide
   - Examples

---

## 📞 Questions to Ask User

- Priorità: CLI o HTTP mode first?
- Sample app: Keep multiple handlers or simplify?
- Testing: Prefer pytest o unittest?
- Docs: MkDocs o Sphinx?

---

**Created**: 2025-11-09
**Next Session**: Implement `_run_cli()` method in Publisher class
