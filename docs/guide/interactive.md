# Interactive Mode

User-friendly parameter prompting with gum.

## Installation

```bash
# Install gum
brew install gum  # macOS

# Install smpub with gum support (NOTA: quota in zsh!)
pip install 'smpub[gum]'
```

## Usage

After registering your app with `smpub add`:

```bash
smpub myapp handler method --interactive
# or short form
smpub myapp handler method -i
```

**Development mode** (without registry):

```bash
python myapp.py handler method --interactive
```

See [Quick Start](../user-guide/quickstart.md) for examples.
