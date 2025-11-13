---
name: Document FastAPI Extension Patterns
about: Document how to add middleware, auth, and custom routes to smpub HTTP server
title: 'docs: Add FastAPI extension guide (middleware, auth, custom routes)'
labels: documentation, priority-high
assignees: ''
---

## Problem

Users think smpub doesn't support middleware, authentication, or custom routes because it's not documented.

**Reality**: smpub uses FastAPI under the hood. You CAN add all FastAPI features.

**Current misconception**: "No middleware chains, no custom auth decorators" is listed as a limitation.

**Truth**: This is **NOT** a limitation, just undocumented.

## Solution

Document how to access and extend the underlying FastAPI app.

## Implementation Checklist

### 1. Update `WHY_SMPUB.md`

- [ ] **Remove** "Complex HTTP patterns" from cons list
- [ ] **Add** new section: "Extending FastAPI"

Add this section after "What smpub Actually Gives You":

```markdown
## Extending FastAPI: Middleware, Auth, and More

**Question**: "Can I add middleware and authentication?"

**Answer**: **Yes!** smpub uses FastAPI under the hood. You have full access to the FastAPI app.

### Example: Adding CORS and Authentication

```python
from smartpublisher.api_server import create_fastapi_app
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# Create your smpub app
app_instance = MyApp()

# Get the FastAPI app
fastapi_app = create_fastapi_app(app_instance)

# Add CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add authentication middleware
@fastapi_app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Skip auth for docs
    if request.url.path in ["/", "/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)

    # Check auth token
    token = request.headers.get("Authorization")
    if not token or not validate_token(token):
        return JSONResponse(
            {"error": "Unauthorized"},
            status_code=401
        )

    # Add user to request state
    request.state.user = get_user_from_token(token)
    return await call_next(request)

# Add custom routes
@fastapi_app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Add route with dependency injection
from fastapi import Depends, Header
from typing import Annotated

def get_current_user(authorization: Annotated[str, Header()]):
    token = authorization.replace("Bearer ", "")
    user = verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@fastapi_app.get("/me")
async def get_user_info(user: Annotated[User, Depends(get_current_user)]):
    return {"username": user.name, "email": user.email}

# Run with custom configuration
import uvicorn
uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
```

### Example: Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
fastapi_app.state.limiter = limiter
fastapi_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@fastapi_app.get("/limited")
@limiter.limit("5/minute")
async def limited_route(request: Request):
    return {"message": "This route is rate-limited"}
```

### Example: Custom Error Handling

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

@fastapi_app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "details": exc.errors(),
            "body": exc.body
        },
    )
```

**Conclusion**: FastAPI's full power is available. smpub doesn't limit you.
```

### 2. Update `docs/appendix/architecture.md`

- [ ] Add to "Extension Points" section:

```markdown
### Extending the FastAPI App

smpub exposes the FastAPI app for full customization:

#### Accessing the FastAPI App

```python
from smartpublisher.api_server import create_fastapi_app

app_instance = MyApp()
fastapi_app = create_fastapi_app(app_instance)

# Now you have a standard FastAPI app
# Add anything FastAPI supports
```

#### Common Extensions

**Middleware**:
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

fastapi_app.add_middleware(CORSMiddleware, allow_origins=["*"])
fastapi_app.add_middleware(GZipMiddleware, minimum_size=1000)
```

**Authentication**:
```python
@fastapi_app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Your auth logic
    return await call_next(request)
```

**Custom Routes**:
```python
@fastapi_app.get("/custom")
async def custom_endpoint():
    return {"custom": "route"}
```

**Dependencies**:
```python
from fastapi import Depends

def get_db():
    # Your DB connection
    pass

@fastapi_app.get("/data")
async def get_data(db = Depends(get_db)):
    return db.query(...)
```

**Event Handlers**:
```python
@fastapi_app.on_event("startup")
async def startup():
    print("Server starting...")

@fastapi_app.on_event("shutdown")
async def shutdown():
    print("Server shutting down...")
```
```

### 3. Create New Doc: `docs/advanced/extending-fastapi.md`

- [ ] Create comprehensive guide with:
  - [ ] Middleware examples (CORS, auth, logging)
  - [ ] Authentication patterns (JWT, OAuth, API keys)
  - [ ] Custom routes and endpoints
  - [ ] Dependency injection
  - [ ] Error handling
  - [ ] Background tasks
  - [ ] WebSocket support
  - [ ] Static file serving
  - [ ] Rate limiting
  - [ ] Custom OpenAPI schema

### 4. Add Examples

- [ ] Create `examples/fastapi_extensions/`:
  - [ ] `middleware_example.py` - CORS, auth, logging
  - [ ] `auth_example.py` - JWT authentication
  - [ ] `custom_routes_example.py` - Additional endpoints
  - [ ] `dependencies_example.py` - Dependency injection
  - [ ] `rate_limiting_example.py` - Rate limiting with slowapi

### 5. Update Comparison Table

- [ ] Update table in `WHY_SMPUB.md`:

Change from:
```
| HTTP patterns | ❌ No middleware | ✅ Full control | ✅ Full control |
```

To:
```
| HTTP patterns | ❌ | ✅ | ✅ Full FastAPI access |
```

## Benefits

✅ **Removes false limitation** from cons list
✅ **Shows FastAPI compatibility** as a strength
✅ **Empowers users** to extend as needed
✅ **Production-ready patterns** documented

## Estimated Effort

**2-3 hours** total:
- Update WHY_SMPUB.md: 30 minutes
- Update architecture.md: 30 minutes
- Create extending-fastapi.md: 1 hour
- Create examples: 1 hour

## Priority

🔥 **HIGH** - Corrects false perception of limitation

## Related Issues

- #1 (Async support) - Uses same FastAPI patterns

## References

- FastAPI middleware: https://fastapi.tiangolo.com/tutorial/middleware/
- FastAPI dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- FastAPI custom routes: https://fastapi.tiangolo.com/tutorial/path-operation-configuration/
