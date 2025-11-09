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
# Register the mail service example app
smpub add mailapp --path ./examples

# Verify registration
smpub list
```

### Step 3: Test Interactive Mode

```bash
# Test 1: Configure mail account (complex signature with defaults)
smpub mailapp mail configure_account --interactive
# You will be prompted:
# smtp_host (str): smtp.gmail.com
# smtp_port (int) [default: 587]: <press enter for default>
# username (str) [default: ]: user@example.com
# use_tls (bool) [True/False]: True
# auth_method (plain, login, oauth2) [default: plain]: plain

# Test 2: Send email with all parameters
smpub mailapp mail send --interactive
# You will be prompted:
# to (str): recipient@example.com
# subject (str): Test email
# body (str): This is a test message
# priority (low, normal, high) [default: normal]: high
# html (bool) [True/False]: False

# Test 3: Send email with short form (using defaults)
smpub mailapp mail send -i
# You will be prompted:
# to (str): another@example.com
# subject (str): Quick message
# body (str): Hello!
# priority (low, normal, high) [default: normal]: <press enter for default>
# html (bool) [True/False]: <press enter for default>

# Test 4: Get current configuration (no parameters)
smpub mailapp mail get_config
```

### Step 4: Verify Results

```bash
# List sent messages
smpub mailapp mail list_sent

# Clear messages
smpub mailapp mail clear_messages
```

### Step 5: Cleanup

```bash
# Remove from registry
smpub remove mailapp

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
smpub mailapp mail send "user@example.com" "Subject" "Body text" high false

# Interactive mode: prompts for each parameter
smpub mailapp mail send --interactive
```

See [CLI Mode](cli-mode.md) for more examples.
