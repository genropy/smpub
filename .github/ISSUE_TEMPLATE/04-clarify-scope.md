---
name: Clarify Project Scope (GraphQL and Web UI)
about: Document what smpub IS and IS NOT designed to do
title: 'docs: Clarify project scope - remove non-limitations from cons'
labels: documentation, priority-low
assignees: ''
---

## Problem

Two items in the cons list are **not limitations**, they're **scope boundaries**:

1. "GraphQL queries: It's REST POST endpoints, period."
2. "Web UI forms: It's CLI/API, not a web framework."

These are like saying "a hammer is not a screwdriver". They're not bugs or limitations - they're the **definition** of what the tool does.

## Solution

**Remove these from cons** and instead add a clear "What smpub IS NOT" section.

## Implementation Checklist

### 1. Update `WHY_SMPUB.md`

- [ ] **Remove** "GraphQL" and "Web UI" from cons list
- [ ] **Add** new section: "What smpub IS and IS NOT"

Add this section after "Should You Use smpub?":

```markdown
## What smpub IS and IS NOT

### What smpub IS

✅ **CLI/API dual exposure framework**: Write methods once, get both CLI and HTTP API.

✅ **Internal tool builder**: Perfect for admin scripts, data pipelines, deployment tools.

✅ **Convention-over-configuration**: Standardized patterns for consistent interfaces.

✅ **FastAPI-powered**: Full FastAPI capabilities available under the hood.

✅ **Type-safe**: Pydantic validation for all parameters.

### What smpub IS NOT

❌ **Not a web framework**: No HTML templates, no sessions, no cookie handling.
- **Use instead**: FastAPI + Jinja2, Flask, Django
- **You CAN**: Connect frontend to smpub's HTTP API

❌ **Not a GraphQL server**: REST POST endpoints only, no GraphQL schema or queries.
- **Use instead**: Strawberry, Ariadne, Graphene
- **Why**: GraphQL is a different paradigm that doesn't align with method-call semantics

❌ **Not a replacement for Click/Typer**: If you ONLY need CLI (no HTTP), use Click/Typer directly.
- **Use smpub when**: You want both CLI and API
- **Use Click when**: You only need CLI and want maximum control

❌ **Not a microservices orchestrator**: It exposes methods, not complex service meshes.
- **Use instead**: Kubernetes, Docker Compose, service mesh tools
- **You CAN**: Run multiple smpub apps as separate services

### Examples of What to Build with smpub

✅ **Good fit**:
- Database admin tools (CLI + API for automation)
- Deployment scripts (run locally or trigger via API)
- Data processing pipelines (CLI for dev, API for production)
- Internal dashboards (API backend + separate frontend)
- DevOps utilities (CLI for ops, API for CI/CD)

❌ **Bad fit**:
- Public-facing web applications (use FastAPI/Flask)
- GraphQL APIs (use Strawberry)
- Complex form-based workflows (use full web framework)
- Real-time chat applications (use WebSocket-focused framework)
- Single-purpose CLI-only tools (use Click/Typer)

### The Sweet Spot

smpub is for **medium-complexity internal tools** where you want:
- Both CLI and HTTP API
- Quick development (no boilerplate)
- Type safety (Pydantic)
- Standard patterns (no custom parsers)

**If your tool is outside this sweet spot**, use the right tool for the job.
```

### 2. Update Cons Section

Change the cons list from:

```markdown
### What smpub Doesn't Give You

❌ **Flexibility in CLI UX**: Standard `--arg value` syntax, not custom parsers.
❌ **Complex HTTP patterns**: No middleware, no custom auth decorators.
❌ **GraphQL queries**: It's REST POST endpoints, period.
❌ **Async handlers**: Currently sync only (async support planned).
❌ **Web UI forms**: It's CLI/API, not a web framework.
```

To:

```markdown
### Actual Limitations

❌ **Opinionated CLI syntax**: Standard `--arg value` pattern. No custom parsers (by design).

❌ **Async handlers**: Not yet supported (planned for v0.2.0).

**Note**: "No middleware" and "No GraphQL" were removed - they're not limitations. See "What smpub IS NOT" for scope clarification.
```

### 3. Add "When NOT to Use smpub" Section

Add after cons:

```markdown
## When NOT to Use smpub

Be honest with yourself. Don't force smpub where it doesn't fit:

### ❌ Skip smpub if:

**Your tool is too simple**:
```python
# This doesn't need smpub
@click.command()
def hello():
    print("Hello!")
```
**Use Click/Typer** - Don't add framework overhead for trivial tools.

---

**You're building a web application**:
```python
# smpub won't help here
@app.get("/")
def home():
    return templates.TemplateResponse("home.html")
```
**Use FastAPI + Jinja2 or Flask** - smpub has no template engine.

---

**You need GraphQL**:
```python
# smpub doesn't do this
type Query {
  user(id: ID!): User
  posts(limit: Int): [Post]
}
```
**Use Strawberry or Ariadne** - smpub is REST-focused.

---

**You need highly custom CLI**:
```python
# smpub can't do this
@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = CustomContext()

@cli.command()
@click.option('--range', type=click.IntRange(1, 100))
def process(range):
    pass
```
**Use Click/Typer** - smpub uses standard `--arg value` syntax.

---

**You only need CLI OR API (not both)**:
- Only CLI? → Use Click/Typer (simpler)
- Only API? → Use FastAPI (more flexible)
- Need both? → **Use smpub**

### ✅ Use smpub when:

You answer YES to all:
1. ☑️ Need both CLI and HTTP API
2. ☑️ Medium complexity (not trivial, not huge)
3. ☑️ Okay with standard CLI syntax
4. ☑️ Working on internal tools (not public web apps)
5. ☑️ Want to eliminate boilerplate

**If you answered NO to any**, consider alternatives.
```

### 4. Update "The Honest Verdict" Section

- [ ] Rewrite to focus on real limitations, not scope:

```markdown
## The Honest Verdict

**Is smpub useful?** Yes, **if you hit its sweet spot**.

**The sweet spot**: Medium-complexity internal tools needing dual CLI/API exposure.

**Real limitations**:
1. Opinionated CLI syntax (no custom parsers)
2. Async support not yet implemented (coming soon)

**Not limitations** (just scope):
- No GraphQL (use Strawberry if you need it)
- No web UI (use FastAPI + templates if you need it)
- No custom CLI parsers (use Click if you need them)

**The question**: Does eliminating dual-interface boilerplate justify learning smpub?

**Answer**: Only if you're writing **multiple** internal tools with dual exposure. One-off tools? Stick with Click + FastAPI separately.
```

## Benefits

✅ **Removes false limitations** from cons
✅ **Sets clear expectations** about scope
✅ **Helps users self-select** the right tool
✅ **Reduces confusion** about what smpub does

## Estimated Effort

**1 hour** total:
- Update WHY_SMPUB.md: 45 minutes
- Review and polish: 15 minutes

## Priority

🟢 **LOW** - Clarification only, not blocking usage

## Related Issues

None

## References

- "Scope is not a limitation" philosophy
- Tools should have clear boundaries
