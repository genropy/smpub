# How SmartSwitch Plugins Reduce Boilerplate Code

This document explains how the smartswitch plugin system (automatically applied by smpub's Publisher) dramatically reduces the amount of code you need to write.

## The Three Auto-Applied Plugins

When you publish a handler with `Publisher.publish()`, three plugins are automatically applied:

1. **LoggingPlugin** - Automatic call tracking
2. **PydanticPlugin** - Automatic parameter validation
3. **SmartasyncPlugin** - Automatic sync/async handling

You don't need to do anything - they're applied retroactively during `publish()`.

## PydanticPlugin: Automatic Validation

### Without PydanticPlugin (Manual Validation)

```python
def add(self, article_type_id, code, description, price):
    # Type validation - 8 lines
    if not isinstance(article_type_id, int):
        return {"success": False, "error": "article_type_id must be int"}
    if not isinstance(code, str):
        return {"success": False, "error": "code must be str"}
    if not isinstance(description, str):
        return {"success": False, "error": "description must be str"}
    if not isinstance(price, (int, float)):
        return {"success": False, "error": "price must be number"}

    # Constraint validation - 2 lines
    if price <= 0:
        return {"success": False, "error": "price must be > 0"}

    # Finally, business logic
    with get_connection() as conn:
        # ... actual work (20 lines)
```

**Total**: 30 lines (10 validation + 20 business logic)

### With PydanticPlugin (Automatic Validation)

```python
from typing import Annotated
from pydantic import Field

def add(
    self,
    article_type_id: int,
    code: str,
    description: str,
    price: Annotated[float, Field(gt=0)]
) -> dict:
    # Business logic directly
    with get_connection() as conn:
        # ... actual work (20 lines)
```

**Total**: 20 lines (0 validation + 20 business logic)

**Savings**: 10 lines per method = 33% less code!

## How It Works

### 1. Type Validation

```python
def add(self, article_type_id: int, code: str, price: float):
    # PydanticPlugin reads type hints and validates:
    # - article_type_id MUST be int
    # - code MUST be str
    # - price MUST be float
    # If validation fails, raises ValidationError before method execution
```

### 2. Constraint Validation

```python
from typing import Annotated
from pydantic import Field

def add(self, price: Annotated[float, Field(gt=0)]):
    # PydanticPlugin enforces constraints:
    # - gt=0: greater than 0
    # - ge=0: greater than or equal to 0
    # - lt=100: less than 100
    # - le=100: less than or equal to 100
    # - min_length=5: for strings
    # - max_length=100: for strings
    # - pattern="^[A-Z]+$": regex validation
```

### 3. Validation Happens BEFORE Method Execution

```
User calls method → PydanticPlugin intercepts → Validates parameters →
If valid: calls method → If invalid: raises ValidationError (method never executes)
```

## Real-World Example from sample_shop

### Articles.add() Method

**Without plugins (manual)**:
```python
def add(self, article_type_id, code, description, price):
    # 10 lines of validation
    if not isinstance(article_type_id, int):
        return {"success": False, "error": "article_type_id must be int"}
    if not isinstance(code, str):
        return {"success": False, "error": "code must be str"}
    if not isinstance(description, str):
        return {"success": False, "error": "description must be str"}
    if not isinstance(price, (int, float)):
        return {"success": False, "error": "price must be float"}
    if price <= 0:
        return {"success": False, "error": "price must be > 0"}

    # Business logic
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM article_types WHERE id = ?", (article_type_id,))
        # ... etc (20 lines)
```

**With plugins (automatic)**:
```python
def add(
    self,
    article_type_id: int,
    code: str,
    description: str,
    price: Annotated[float, Field(gt=0)]
) -> dict:
    # Business logic directly - no validation needed!
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM article_types WHERE id = ?", (article_type_id,))
        # ... etc (20 lines)
```

## LoggingPlugin: Automatic Call Tracking

All method calls are automatically logged (in silent mode by default):

```python
class Articles:
    def add(self, article_type_id, code, description, price):
        # LoggingPlugin automatically tracks:
        # - Method name called
        # - Parameters received
        # - Return value
        # - Execution time
        # - Any exceptions raised
        pass
```

No need to add `logger.info()` calls everywhere!

## SmartasyncPlugin: Automatic Sync/Async

Methods work in both synchronous and asynchronous contexts automatically:

```python
class Articles:
    def add(self, article_type_id, code, description, price):
        # This method works in both:
        # 1. Synchronous: result = articles.add(...)
        # 2. Asynchronous: result = await articles.add(...)
        pass
```

No need to write separate `async def` versions!

## Code Savings Summary

For the **sample_shop** example:

- **ArticleTypes**: 4 methods × 5 lines = 20 lines saved
- **Articles**: 5 methods × 8 lines = 40 lines saved
- **Purchases**: 5 methods × 6 lines = 30 lines saved

**Total: 90 lines of boilerplate eliminated!**

And this is a small example. In a real application with 50+ methods, you could save **500+ lines** of validation code.

## Best Practices

### 1. Use Type Hints Always

```python
# Good
def add(self, code: str, price: float) -> dict:
    pass

# Bad
def add(self, code, price):
    pass
```

### 2. Use Field for Constraints

```python
from typing import Annotated
from pydantic import Field

# Good - declarative constraints
def add(self, price: Annotated[float, Field(gt=0, le=10000)]):
    pass

# Bad - imperative checks
def add(self, price: float):
    if price <= 0:
        return {"error": "price must be > 0"}
    if price > 10000:
        return {"error": "price must be <= 10000"}
```

### 3. Focus on Business Logic

Let plugins handle:
- Type checking
- Range validation
- String constraints
- Logging
- Async handling

You focus on:
- Business rules
- Database operations
- Application logic

## Advanced Field Constraints

```python
from typing import Annotated
from pydantic import Field

# Numeric constraints
price: Annotated[float, Field(gt=0, le=10000)]
quantity: Annotated[int, Field(ge=1, le=1000)]
discount: Annotated[float, Field(ge=0.0, le=1.0)]

# String constraints
code: Annotated[str, Field(min_length=3, max_length=20)]
email: Annotated[str, Field(pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$")]
phone: Annotated[str, Field(pattern=r"^\+?1?\d{9,15}$")]

# With descriptions (shown in OpenAPI docs)
name: Annotated[str, Field(min_length=1, max_length=100, description="Article name")]
```

## Conclusion

The smartswitch plugin system, automatically applied by smpub's Publisher, transforms this:

```python
# 40 lines: 20 validation + 20 business logic
def method(self, param1, param2, param3):
    if not isinstance(param1, int):
        return error
    if not isinstance(param2, str):
        return error
    if param3 <= 0:
        return error
    # ... 10 more lines of validation
    # ... 20 lines of business logic
```

Into this:

```python
# 20 lines: 0 validation + 20 business logic
def method(self, param1: int, param2: str, param3: Annotated[float, Field(gt=0)]):
    # ... 20 lines of business logic
```

**Write less. Validate more. Focus on what matters.**
