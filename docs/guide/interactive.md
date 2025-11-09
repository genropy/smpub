# Interactive Mode

User-friendly parameter prompting with gum.

## Installation

```bash
# 1. Install gum
brew install gum  # macOS

# 2. Install smpub with gum support (NOTA: quota in zsh!)
pip install 'smpub[gum]'
```

## Complete Test Sequence

### Step 1: Install and Setup

```bash
# From smpub project root
cd /path/to/smpub

# Install in development mode
pip install -e .

# Verify smpub command is available
which smpub
```

### Step 2: Register Test App

```bash
# Register the calculator example app
smpub add calculator --path ./examples

# Verify registration
smpub list
```

### Step 3: Test Interactive Mode

```bash
# Test 1: Simple addition (interactive prompts for both parameters)
smpub calculator calc add --interactive
# You will be prompted:
# a (int): 10
# b (int): 20
# Result: 30

# Test 2: Short form
smpub calculator calc add -i

# Test 3: Multiplication with default value
smpub calculator calc multiply --interactive
# You will be prompted:
# x (float): 5.5
# y (float) [default: 2.0]: <press enter for default>
# Result: 11.0

# Test 4: Complex signature with Literal and boolean
smpub add testcomplex --path ./examples
smpub testcomplex tasks create --interactive
# You will be prompted:
# title (str): Fix bug
# priority (low, medium, high): high
# max_retries (int) [default: 3]: 5
# notify (bool) [True/False]: true
```

### Step 4: Verify Results

```bash
# List created tasks
smpub testcomplex tasks list

# Clear tasks
smpub testcomplex tasks clear
```

### Step 5: Cleanup

```bash
# Remove from registry
smpub remove calculator
smpub remove testcomplex

# Verify removal
smpub list
```

## What Happens

1. **`--interactive` flag** triggers gum prompts
2. **For each parameter**:
   - String: Text input
   - Int/Float: Numeric input with validation
   - Boolean: Choose True/False
   - Literal: Choose from allowed values
3. **Default values** shown in square brackets
4. **Validation** happens after all inputs collected
5. **Method executes** with validated parameters

## Interactive vs Normal Mode

```bash
# Normal mode: all arguments on command line
smpub calculator calc add 10 20

# Interactive mode: prompts for each parameter
smpub calculator calc add --interactive
```

See [CLI Mode](cli-mode.md) for more examples.
