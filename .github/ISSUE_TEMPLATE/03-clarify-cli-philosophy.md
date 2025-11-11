---
name: Clarify CLI Philosophy and Flexibility
about: Document CLI design choices and SmartSwitch capabilities
title: 'docs: Clarify CLI syntax philosophy and SmartSwitch features'
labels: documentation, priority-medium
assignees: ''
---

## Problem

The cons list says "Flexibility in CLI UX: You get standard `--arg value` syntax, not custom parsers."

This is **partially true**, but:
1. **Not properly explained** as a design choice (convention over configuration)
2. **Undersells SmartSwitch** hierarchical dispatch capabilities
3. **Doesn't mention** interactive mode as an alternative

Users might think smpub is "limited" when actually it's **opinionated by design**.

## Solution

Document the CLI philosophy and show what IS possible with SmartSwitch.

## Implementation Checklist

### 1. Update `WHY_SMPUB.md`

- [ ] **Rewrite** CLI flexibility con with better context
- [ ] **Add** new section: "CLI Philosophy"

Change from:
```markdown
❌ **Flexibility in CLI UX**: You get standard `--arg value` syntax, not custom parsers.
```

To:
```markdown
❌ **Opinionated CLI syntax**: Standard `--arg value` pattern for all parameters. No custom parsers (by design).

**Why this is intentional**:
- Enables automatic API generation (custom parsers break this)
- Reduces cognitive load (same pattern everywhere)
- Sufficient for 95% of internal tools

**What you CAN do**:
- ✅ Hierarchical commands via SmartSwitch (`app handler method --args`)
- ✅ Interactive mode with Textual TUI (`--interactive`)
- ✅ Type validation and conversion
- ✅ Help text from docstrings

**If you need custom CLI parsing**, use Click/Typer directly. smpub prioritizes **dual CLI/API exposure** over CLI flexibility.
```

### 2. Add "CLI Philosophy" Section to `WHY_SMPUB.md`

Add after "How it Works":

```markdown
## CLI Philosophy: Convention Over Configuration

### The Trade-off

smpub makes a deliberate choice: **standardize CLI syntax to enable automatic API generation**.

**Standard syntax**:
```bash
# All parameters use --flag value
smpub app handler method --param1 value1 --param2 value2

# Interactive mode for complex inputs
smpub app handler method --interactive
```

**What you DON'T get**:
- Custom argument types (Click's IntRange, Path, Choice)
- Complex context passing between commands
- Custom help formatting beyond docstrings

**What you DO get**:
- Write method once, get CLI + HTTP API
- Consistent interface across all methods
- Automatic type validation (Pydantic)
- Interactive TUI for guided input

### When to Use Standard CLI vs Custom

**Use smpub when**:
- You want both CLI and HTTP
- Standard `--arg value` is sufficient
- You value quick development

**Use Click/Typer when**:
- You ONLY need CLI
- You need custom types (e.g., Path validation)
- You need complex command hierarchies with context

### SmartSwitch Power

smpub uses SmartSwitch for hierarchical command dispatch:

```python
class UserHandler(PublishedClass):
    api = ApiSwitcher(prefix='user_')

    @api
    def create(self, name: str, email: str) -> str:
        """Create a new user."""
        return f"Created user {name}"

    @api
    def delete(self, user_id: int) -> str:
        """Delete a user."""
        return f"Deleted user {user_id}"

class AdminHandler(PublishedClass):
    api = ApiSwitcher(prefix='admin_')

    @api
    def promote(self, user_id: int) -> str:
        """Promote user to admin."""
        return f"User {user_id} is now admin"
```

CLI usage:
```bash
# Hierarchical dispatch
smpub app user create --name Alice --email alice@example.com
smpub app user delete --user-id 123
smpub app admin promote --user-id 123

# Same methods via HTTP
curl -X POST http://localhost:8000/user/create \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

**Hierarchy is automatic**. No need to configure routes or subcommands.
```

### 3. Add to `docs/appendix/architecture.md`

- [ ] Add SmartSwitch capabilities section:

```markdown
## SmartSwitch Dispatch

### Hierarchical Command Structure

SmartSwitch provides automatic hierarchical dispatch:

```python
class EmailHandler(PublishedClass):
    api = ApiSwitcher(prefix='email_')

    @api
    def send(self, to: str, subject: str) -> str:
        """Send email."""
        pass

    @api
    def list_sent(self, limit: int = 10) -> list:
        """List sent emails."""
        pass

class TemplateHandler(PublishedClass):
    api = ApiSwitcher(prefix='template_')

    @api
    def create(self, name: str, body: str) -> str:
        """Create template."""
        pass
```

CLI dispatch:
```bash
app email send --to user@example.com --subject "Hello"
app email list-sent --limit 20
app template create --name welcome --body "Welcome {{name}}"
```

HTTP endpoints:
```
POST /email/send
POST /email/list_sent
POST /template/create
```

**No explicit routing configuration**. SmartSwitch handles it.

### Method Name Resolution

SmartSwitch supports multiple name formats:

```python
@api
def send_email(self, to: str) -> str:
    pass
```

Can be called as:
- `app handler send-email --to user@example.com` (kebab-case)
- `app handler send_email --to user@example.com` (snake_case)
- `POST /handler/send_email` (HTTP always uses snake_case)

### Prefix Patterns

Use prefixes to avoid name collisions:

```python
class UserHandler(PublishedClass):
    api = ApiSwitcher(prefix='user_')

    @api
    def list(self) -> list:  # Becomes 'user_list'
        pass

class OrderHandler(PublishedClass):
    api = ApiSwitcher(prefix='order_')

    @api
    def list(self) -> list:  # Becomes 'order_list'
        pass
```

CLI:
```bash
app user list
app order list
```

HTTP:
```
POST /user/list
POST /order/list
```
```

### 4. Add Interactive Mode Documentation

- [ ] Add to WHY_SMPUB.md:

```markdown
### Interactive Mode: The CLI Alternative

For complex parameters, smpub provides **interactive mode** with Textual TUI:

```bash
# Launch interactive form
smpub app handler method --interactive
```

Features:
- ✅ Type-aware input fields
- ✅ Real-time validation
- ✅ Default values shown
- ✅ Boolean checkboxes
- ✅ Rich terminal UI

This is better than custom CLI parsers for:
- Long text inputs
- Multiple optional parameters
- Complex data entry
- User-friendly guided workflows
```

### 5. Update Comparison Table

- [ ] Update table in WHY_SMPUB.md:

| Feature | Click/Typer | FastAPI | smpub | FastAPI + Typer |
|---------|-------------|---------|-------|-----------------|
| CLI interface | ✅ Custom parsers | ❌ | ✅ Standard syntax | ✅ Custom parsers |
| Hierarchical commands | ✅ Complex | ❌ | ✅ Automatic (SmartSwitch) | ✅ Complex |
| Interactive TUI | ❌ | ❌ | ✅ Built-in | ❌ |

## Benefits

✅ **Clarifies design choice** (not a limitation)
✅ **Shows SmartSwitch power** (hierarchical dispatch)
✅ **Highlights interactive mode** as alternative
✅ **Sets expectations** for the right use cases

## Estimated Effort

**1-2 hours** total:
- Update WHY_SMPUB.md: 45 minutes
- Update architecture.md: 45 minutes
- Add SmartSwitch examples: 30 minutes

## Priority

🟡 **MEDIUM** - Clarifies philosophy, but not blocking

## Related Issues

None

## References

- SmartSwitch documentation: https://github.com/genropy/smartswitch
- Textual documentation: https://textual.textualize.io/
