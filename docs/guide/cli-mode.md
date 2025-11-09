# CLI Mode

Command-line interface for your handlers.

## Registry Usage (Recommended)

First, register your app:

```bash
smpub add myapp --path /path/to/myapp
```

Then use it:

```bash
smpub myapp <handler> <method> [args...]
```

## Help

```bash
# Registry management
smpub --help
smpub list
smpub list --global

# App help
smpub myapp --help

# Handler help
smpub myapp <handler> --help
```

## Development Mode (Direct Execution)

For testing during development, you can run directly:

```bash
python myapp.py <handler> <method> [args...]
python myapp.py --help
```

See [Quick Start](../user-guide/quickstart.md) for examples.
