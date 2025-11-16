# Level 1: Repository Skeleton

## 🎯 Learning Objectives

This level teaches the **foundations** of building a smartpublisher application:

1. **Class with Switcher** - How to define an API surface
2. **Method signatures** - Define interfaces before implementation
3. **SmartSwitch dispatch** - How method routing works
4. **Skeleton/Stub development** - Start with structure, implement later
5. **Library-first approach** - Build library, then publish

## 📚 What's Included

### `src/repository.py`
The **Repository** class with:
- Switcher for method dispatch
- Three API methods (skeleton/stub):
  - `branches()` - List branches
  - `history(limit)` - Get commit history
  - `info()` - Get repo metadata
- Type hints for all parameters and returns
- Docstrings explaining what each method will do

**Key Point**: Methods return placeholder data - they don't call real APIs yet!

### `app/test_repo.py`
Shows how to use Repository as a **Python library**:
```python
from src.repository import Repository

repo = Repository("smartpublisher", "https://github.com/genropy/smartpublisher.git")

# Call methods through Switcher
branches = Repository.api("branches")(repo)
commits = Repository.api("history")(repo, limit=5)
info = Repository.api("info")(repo)
```

### `published_app/main.py`
Shows how to **publish** Repository with smartpublisher:
```python
from smartpublisher import Publisher
from src.repository import Repository

class RepoApp(Publisher):
    def on_init(self):
        repo = Repository("smartpublisher", "https://...")
        self.publish('repo', repo)
```

**Result**: Automatic CLI + HTTP interface!

## 🔑 Key Concepts

### 1. Switcher Pattern
```python
class Repository:
    api = Switcher()

    @api
    def branches(self): ...
```

The `@api` decorator registers methods with the Switcher.
Method names are direct and concise: `branches()`, `history()`, `info()`.

### 2. Skeleton Development
Methods can be stubs (return empty/placeholder data) while you:
- Design the API
- Write tests
- Build the frontend/CLI
- Implement incrementally

### 3. Library-First
The Repository class is a **pure Python library**:
- No dependency on smartpublisher
- Uses SmartSwitch for clean dispatch
- Can be used directly in Python code

The Publisher is a **thin layer** that exposes the library via CLI/HTTP.

## 🧪 Try It

### As Python Library
```bash
cd app
python test_repo.py
```

You'll see:
- Repository creation
- Method calls through Switcher
- Placeholder data returned
- API introspection

### As Published App (CLI)
```bash
cd published_app
python main.py repo branches
python main.py repo history --limit 5
python main.py repo info
```

Even with skeleton methods, you get a working CLI!

### As Published App (HTTP)
```bash
cd published_app
python main.py
```

Then open: http://localhost:8000/docs

You'll see:
- OpenAPI/Swagger UI
- All three endpoints
- Try them out (they return skeleton data)

## 📊 What You'll Learn

| Concept | What You See |
|---------|--------------|
| **Switcher** | Method routing and dispatch |
| **@api decorator** | Method registration |
| **Type hints** | Parameter and return types |
| **Skeleton methods** | API design before implementation |
| **SmartSwitch introspection** | describe() method |
| **Publisher pattern** | Library → CLI/HTTP |

## 🎓 Next Steps

After understanding this level:
1. **Level 2**: Implement the methods with real GitHub API calls
2. **Level 3**: Add Project class to manage multiple repositories
3. **Level 4**: Add Commander class for full application

## 💡 Key Takeaway

You can **design and publish APIs** before implementing them!

This enables:
- ✅ API-first development
- ✅ Test-driven development (TDD)
- ✅ Parallel frontend/backend work
- ✅ Rapid prototyping
- ✅ Contract-first design

The skeleton approach lets you:
1. Define the interface
2. Get feedback
3. Test the structure
4. Implement incrementally
