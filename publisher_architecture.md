# Publisher Architecture

## Core Principle: Publisher is a Published App

**Key insight**: Publisher is not a special meta-object outside the ecosystem. Publisher is a **normal app** with a specific task (publishing other apps) and commands to execute that task.

Therefore: **Publisher IS a PublishedClass**.

## Entry Point Architecture

Publisher is the **primary module** for CLI entry. The flow is:

1. Shell executes `smpub` command
2. Pip invokes `smartpublisher.publisher:main` (module-level function)
3. `main()` creates `Publisher()` instance
4. Calls `publisher.run_cli()` (instance method)
5. Which delegates to CLI channel: `self.chan_registry['cli'].run(sys.argv[1:])`

**Key point**: `cli.py` is an **auxiliary module** (the CLI channel implementation), not the entry point.

### Reasoning
1. Any app has a task and commands to execute it
2. Publisher is an app with the task of publishing apps
3. Publisher receives commands to manage apps and channels
4. → Publisher is a published app

## Special Status: The Root App (`.self`)

Publisher is the **root app** - the implicit `.self` that doesn't need to be registered:

- **Normal apps**: `smpub myapp quit` (explicit app name)
- **Publisher**: `smpub quit` (`.self` is implicit)

`.self` is the **initial discontinuity point** - the starting point of the system that contains everything else.

## Inheritance Structure

```python
class Publisher(PublishedClass):
    """
    Publisher is a PublishedClass (not just RoutedClass).
    It's an app like any other, but it's the root app.
    """

    # Override Router to add logging plugin
    api = Router(name='publisher').plug("logging").plug("pydantic")
```

**What Publisher inherits from PublishedClass**:
- `_system` commands (list_handlers, get_handler_info, get_api_tree)
- `published_instances` dictionary (will contain only `_system`)
- Automatic help via `api.describe()`
- Lifecycle hooks infrastructure
- `publish()` method (not used by Publisher, but available)

## Initialization Pattern

```python
def __init__(self, registry_path: Path = None, use_global: bool = False):
    super().__init__()
    self.app_registry = AppRegistry(self, registry_path=registry_path, use_global=use_global)
    self.chan_registry = ChanRegistry(self)
```

**Order matters**:
1. First: `super().__init__()` initializes PublishedClass
2. Then: initialize registries as internal attributes

## Delegation Pattern: Thin Facade

Publisher is a **thin facade** that only delegates to registries:

- **app_registry**: Manages app registration, loading, unloading
- **chan_registry**: Manages channels (CLI, HTTP, etc.)

Publisher does NOT contain business logic for these tasks. It only:
1. Holds references to registries
2. Delegates commands to registries
3. Provides its own lifecycle methods

### Naming Consistency
- `self.app_registry` (NOT `self.registry`)
- `self.chan_registry`
- Clear, explicit naming for both registries

## Registry Initialization

Both registries take `publisher` as first parameter and self-initialize:

```python
# AppRegistry
def __init__(self, publisher, registry_path: Path = None, use_global: bool = False):
    self._publisher = publisher
    # ... self-initialize completely

# ChanRegistry
def __init__(self, publisher):
    self._publisher = publisher
    # ... autodiscover and create channels
```

**Principle**: Each object must know how to initialize, work, and cleanup itself.

## Workspace Structure

Publisher uses `.smpub/` directory for persistence:

- **Local registry**: `.smpub/registry.json` (current directory)
- **Global registry**: `~/.smpub/registry.json` (home directory)
- **No intermediate directories** (removed `~/.smartlibs/publisher/`)

Simple, flat structure for both local and global registries.

## Command Structure

Publisher exposes commands at different levels:

### Direct Publisher Commands (`.self` implicit)
```bash
smpub quit           # Publisher.quit() - stop all channels
smpub serve cli      # Publisher.serve('cli') - start CLI channel
smpub serve http     # Publisher.serve('http', port=8000) - start HTTP
```

### App Registry Commands (`.apps` namespace)
```bash
smpub .apps list          # app_registry.list()
smpub .apps add myapp ... # app_registry.add(...)
smpub .apps remove myapp  # app_registry.remove(...)
```

### Channel Registry Commands (`.chan` namespace)
```bash
smpub .chan list          # chan_registry.get_available_channels()
# ... other channel management commands
```

### System Commands (inherited from PublishedClass)
```bash
smpub _system list_handlers     # List all handlers (should show _system only)
smpub _system get_api_tree      # Get complete API tree
```

## Publisher Methods

Publisher provides these method categories:

### 1. Delegation Methods (delegate to registries)
- `load_app(app_name)` → `app_registry.load(app_name)`
- `unload_app(app_name)` → `app_registry.unload(app_name)`
- `get_channel(name)` → `chan_registry.get(name)`

### 2. Lifecycle Methods (Publisher's own logic)
- `serve(channel, **kwargs)` - Start a channel server
- `quit()` - Stop all channels and cleanup
- (Future: `start()`, `stop()`, `restart()`)

### 3. Inherited Methods (from PublishedClass)
- `_system.list_handlers()` - Introspection
- `_system.get_api_tree()` - API schema
- Help via `api.describe()`

## Router Configuration

Publisher's Router has both pydantic and logging plugins:

```python
api = Router(name='publisher').plug("logging").plug("pydantic")
```

- **pydantic**: Inherited from PublishedClass, for validation
- **logging**: Added by Publisher, for operation logging

## Relationship with Other Components

```
Publisher (root app, .self)
├── app_registry (internal attribute)
│   └── manages: app registration, loading, unloading
├── chan_registry (internal attribute)
│   └── manages: channel discovery, instantiation
└── _system (published handler, from PublishedClass)
    └── provides: introspection commands
```

Publisher coordinates but does not contain implementation logic.

## Design Principles Summary

1. **Publisher is an app** (PublishedClass), not a special meta-object
2. **Publisher is the root app** (`.self` implicit)
3. **Thin facade pattern** (delegates everything to registries)
4. **Self-managing objects** (each object initializes, works, cleans up itself)
5. **Naming consistency** (`app_registry`, `chan_registry`)
6. **Clean separation** (Publisher coordinates, registries implement)

## Future Extensions

Publisher can be extended with:
- Additional lifecycle methods (start, stop, restart)
- Configuration management
- Plugin system
- Event system
- Monitoring/metrics

All following the same principles:
- Delegate to specialized components
- Keep Publisher thin
- Maintain clean separation of concerns
