# Git Sample - Progressive Tutorial

## 📚 Overview

This is a **progressive tutorial** demonstrating how to build a Git Repository Manager using **smartpublisher** and **smartswitch**.

The tutorial is organized in **levels**, each building on the previous one. Each level teaches specific concepts and can be studied independently.

## 🎯 Learning Path

### Level 1: Repository Skeleton (`level_1_reposkeleton/`)

**What you'll learn:**
- How to define an API surface with `Switcher`
- Skeleton/stub development approach
- SmartSwitch dispatch mechanism
- Library-first philosophy
- How to publish with ~10 lines of code

**Key concepts:**
- `@api` decorator for method registration
- Prefix stripping (`repo_get_branches` → `get_branches`)
- Method calling pattern: `Class.api("method_name")(instance)`
- Tests work even with stub methods
- Introspection via `describe()`

**Status:** ✅ Complete

[📖 Read Level 1 Documentation](level_1_reposkeleton/doc/README.md)

---

### Level 2: Repository Implementation (`level_2_repo_implemented/`)

**What you'll learn:**
- Implementing real GitHub API calls
- Using requests library for HTTP APIs
- Token-based authentication
- Error handling and retries
- Testing with real API responses

**Key concepts:**
- GitHub REST API integration
- Environment variable configuration (GITHUB_TOKEN)
- Response parsing and data models
- Public vs private repository access

**Status:** 🚧 Planned

---

### Level 3: Project Manager (`level_3_project/`)

**What you'll learn:**
- Managing multiple repositories
- Hierarchical API structure
- Composition with SmartSwitch
- Project-level operations
- Configuration management

**Key concepts:**
- Project class with multiple Repository instances
- Batch operations across repositories
- Project configuration files
- API composition and delegation

**Status:** 🚧 Planned

---

### Level 4: Git Commander (`level_4_commander/`)

**What you'll learn:**
- Building complete application hierarchy
- Commander pattern
- Registry of projects
- Full CLI/HTTP application
- Advanced dispatching

**Key concepts:**
- GitCommander root class
- Project registry management
- Three-level hierarchy (Commander → Project → Repository)
- Complete application lifecycle

**Status:** 🚧 Planned

---

## 📂 Directory Structure

Each level follows the same structure:

```
level_N_name/
├── src/            # Library implementation (pure Python)
├── doc/            # Documentation and learning materials
├── app/            # Python library usage examples
├── published_app/  # Published as CLI/HTTP (using Publisher)
└── tests/          # Test suite for the level
```

This structure emphasizes the **library-first approach**:
1. Write the library in `src/`
2. Use it as Python library in `app/`
3. Publish it with Publisher in `published_app/`
4. Test it in `tests/`

## 🚀 Getting Started

### Prerequisites

```bash
# Install smartpublisher (includes smartswitch)
pip install smartpublisher

# For Level 2+: Set GitHub token for private repos (optional)
export GITHUB_TOKEN="your_github_token"
```

### Recommended Path

1. **Start with Level 1** - Understand the foundation
   ```bash
   cd level_1_reposkeleton

   # Try as Python library
   cd app && python test_repo.py

   # Try published version (CLI)
   cd ../published_app
   python main.py repo get-branches

   # Try published version (HTTP)
   python main.py
   # Open http://localhost:8000/docs

   # Run tests
   cd ../tests && pytest
   ```

2. **Progress through levels** - Each level adds complexity
3. **Study the code** - Each level's `doc/README.md` explains concepts
4. **Run the tests** - Tests document expected behavior
5. **Experiment** - Modify and extend the examples

## 💡 Key Philosophy

### Library-First Development

The examples demonstrate that you should:
1. **Write a Python library** (with SmartSwitch for dispatch)
2. **Use it directly** in your Python code
3. **Optionally publish** it as CLI/HTTP with Publisher

**Not the other way around!** Don't start with Publisher and add library code. The library should work standalone.

### Skeleton Development

Level 1 shows that you can:
- Define API structure before implementation
- Get tests working with stubs
- Build CLI/HTTP interfaces for skeletons
- Implement incrementally

This enables:
- ✅ API-first development
- ✅ Test-driven development (TDD)
- ✅ Parallel frontend/backend work
- ✅ Early feedback on API design

## 📖 Additional Resources

- [smartpublisher Documentation](https://github.com/genropy/smartpublisher)
- [smartswitch Documentation](https://github.com/genropy/smartswitch)
- [More Examples](https://github.com/genropy/smartpublisher-examples)

## 🎓 Learning Outcomes

By completing this tutorial series, you'll understand:

- ✅ How to design APIs with SmartSwitch
- ✅ Library-first development approach
- ✅ Skeleton/stub development workflow
- ✅ Publishing Python libraries as CLI/HTTP
- ✅ Hierarchical API composition
- ✅ Testing dispatch mechanisms
- ✅ GitHub API integration
- ✅ Building real-world applications

## 🤝 Contributing

Found an issue or have suggestions? Open an issue or PR in the [smartpublisher repository](https://github.com/genropy/smartpublisher).

---

**Note**: This tutorial series is designed to be progressive. Don't skip levels - each builds essential understanding for the next!
