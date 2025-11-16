# Feature Request: Multi-App HTTP Server & Auto-Wrapping

## Summary

Enhance `smpub` CLI with four major features:
1. **Auto-wrap Switcher classes** - Automatically wrap classes with `api = Switcher()` in Publisher
2. **Multi-app HTTP server** - Serve multiple apps on one port with different paths
3. **Daemon server** - Run HTTP server as background daemon with management commands
4. **Server dashboard** - HTML dashboard showing status, mounted apps, and controls

## Motivation

**Current limitations:**
- Apps must explicitly inherit from `Publisher` to use `smpub`
- Each app requires its own port when serving HTTP
- Server blocks terminal when running
- No visibility into server status or mounted apps

**Use case:**
Developer working on multiple SmartSwitch-based libraries wants to:
- Quickly test libraries without creating Publisher wrapper
- Run multiple app APIs on single port during development
- Keep terminal available while server runs
- See which apps are mounted and restart server when adding new apps

## Feature 1: Auto-Wrap Switcher Classes

### Description

Allow `smpub add` to register classes that have `api = Switcher()` but don't inherit from Publisher. The system automatically wraps them in a Publisher at load time.

### Implementation

**Registry changes:**
```json
{
  "apps": {
    "myapp": {
      "path": "/path/to/app",
      "module": "myapp",
      "class": "MyApp",
      "type": "switcher"  // New field: "publisher" or "switcher"
    }
  }
}
```

**Discovery enhancement** (`discover_publisher_class()`):
```python
# Current: Only finds Publisher subclasses
pattern = r"class\s+(\w+)\s*\([^)]*Publisher[^)]*\)\s*:"

# New: Also find classes with Switcher
switcher_pattern = r"class\s+(\w+)\s*.*:\s*\n\s+api\s*=\s*Switcher\("
```

**Auto-wrapping** (`load_app()`):
```python
if app_info.get("type") == "switcher":
    # Create dynamic Publisher wrapper
    from smartpublisher import Publisher

    class AutoWrapper(Publisher):
        def __init__(self):
            super().__init__()
            handler = app_class()
            self.publish(handler)

    return AutoWrapper()
```

### Usage

```bash
# Works with Publisher (as before)
cd ~/projects/myapp
smpub add myapp
smpub myapp --help

# Now also works with Switcher-only classes
cd ~/projects/mylib  # Has class with api = Switcher()
smpub add mylib
smpub mylib --help   # Auto-wrapped in Publisher
```

## Feature 2: Multi-App HTTP Server

### Description

Serve multiple apps on a single port, each mounted at different paths. Apps are registered with `--http` flag and optional custom path.

### Implementation

**Registry changes:**
```json
{
  "apps": {
    "shop": {
      "path": "/path/to/shop",
      "module": "shop",
      "class": "Shop",
      "http": true,              // New: Enable HTTP serving
      "http_path": "/shop"       // New: Mount path (defaults to app name)
    },
    "demo": {
      "path": "/path/to/demo",
      "module": "demo",
      "class": "Demo",
      "http": true,
      "http_path": "/demo"
    }
  }
}
```

**Server implementation:**
```python
def serve(port):
    """Start multi-app HTTP server."""
    registry = load_registry()
    main_app = FastAPI()

    # Mount all apps with http: true
    for name, info in registry["apps"].items():
        if info.get("http"):
            app_instance = load_app(name)
            sub_app = create_fastapi_app(app_instance)
            path = info.get("http_path", f"/{name}")
            main_app.mount(path, sub_app)

    # Add dashboard at root
    @main_app.get("/")
    async def dashboard():
        return HTMLResponse(render_dashboard(registry, port))

    uvicorn.run(main_app, host="0.0.0.0", port=port)
```

### Usage

```bash
# Register apps for HTTP serving
smpub add shop --http                    # Mounts at /shop
smpub add demo --http --http-path /api   # Custom path /api

# Start multi-app server
smpub serve 8000

# Access apps
curl http://localhost:8000/shop/product/list
curl http://localhost:8000/api/status

# View dashboard
open http://localhost:8000/
```

## Feature 3: Daemon Server & Management

### Description

Run HTTP server as background daemon, freeing terminal. Management commands to control server lifecycle.

### Implementation

**PID file** (`.smpub_server.pid`):
```json
{
  "pid": 12345,
  "port": 8000,
  "started": "2025-11-13T10:30:00",
  "log_file": ".smpub_server.log"
}
```

**Daemon mode:**
```python
def serve_daemon(port):
    """Start server as daemon."""
    import subprocess

    # Start uvicorn as detached process
    proc = subprocess.Popen(
        [sys.executable, "-m", "smartpublisher._server", str(port)],
        stdout=open(".smpub_server.log", "a"),
        stderr=subprocess.STDOUT,
        start_new_session=True  # Detach from terminal
    )

    # Save PID
    with open(".smpub_server.pid", "w") as f:
        json.dump({
            "pid": proc.pid,
            "port": port,
            "started": datetime.now().isoformat(),
            "log_file": ".smpub_server.log"
        }, f)

    print(f"✓ Server started on port {port} (PID: {proc.pid})")
```

**Management commands:**
```python
def serve_stop():
    """Stop daemon server."""
    with open(".smpub_server.pid") as f:
        info = json.load(f)

    os.kill(info["pid"], signal.SIGTERM)
    os.remove(".smpub_server.pid")
    print(f"✓ Server stopped (PID: {info['pid']})")

def serve_restart():
    """Restart daemon server."""
    with open(".smpub_server.pid") as f:
        info = json.load(f)

    port = info["port"]
    serve_stop()
    serve_daemon(port)
    print(f"✓ Server restarted on port {port}")

def serve_status():
    """Show server status."""
    if not os.path.exists(".smpub_server.pid"):
        print("Server not running")
        return

    with open(".smpub_server.pid") as f:
        info = json.load(f)

    # Check if process is alive
    try:
        os.kill(info["pid"], 0)
        print(f"Server running on port {info['port']} (PID: {info['pid']})")
    except OSError:
        print("Server not running (stale PID file)")

def serve_logs(lines=50):
    """Show server logs."""
    with open(".smpub_server.pid") as f:
        info = json.load(f)

    # Show last N lines
    subprocess.run(["tail", "-n", str(lines), info["log_file"]])
```

### Usage

```bash
# Start server daemon (returns immediately)
smpub serve 8000
# ✓ Server started on port 8000 (PID: 12345)

# Terminal is free, continue working
smpub add newapp --http

# Restart server to load new app
smpub serve restart
# ✓ Server stopped (PID: 12345)
# ✓ Server started on port 8000 (PID: 12346)

# Check status
smpub serve status
# Server running on port 8000 (PID: 12346)

# View logs
smpub serve logs

# Stop server
smpub serve stop
# ✓ Server stopped (PID: 12346)
```

## Feature 4: Server Dashboard

### Description

HTML dashboard at `http://localhost:8000/` showing server status, mounted apps, and management controls.

### Implementation

```python
def render_dashboard(registry, port):
    """Generate HTML dashboard."""
    pid_info = json.load(open(".smpub_server.pid"))

    # Calculate uptime
    started = datetime.fromisoformat(pid_info["started"])
    uptime = datetime.now() - started

    # List mounted apps
    mounted_apps = [
        (name, info)
        for name, info in registry["apps"].items()
        if info.get("http")
    ]

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>SmartPublisher Server</title>
        <style>
            body {{ font-family: monospace; padding: 20px; }}
            .status {{ color: green; }}
            .app-list {{ margin: 20px 0; }}
            button {{ padding: 10px; margin: 5px; cursor: pointer; }}
        </style>
    </head>
    <body>
        <h1>📊 SmartPublisher Server Dashboard</h1>

        <div class="status">
            <strong>Status:</strong> 🟢 Running<br>
            <strong>Port:</strong> {port}<br>
            <strong>PID:</strong> {pid_info["pid"]}<br>
            <strong>Uptime:</strong> {uptime}
        </div>

        <h2>📋 Mounted Apps</h2>
        <ul class="app-list">
    """

    for name, info in mounted_apps:
        path = info.get("http_path", f"/{name}")
        html += f"""
            <li>
                <strong>{path}</strong> ({name})
                - <a href="{path}/docs" target="_blank">Swagger UI</a>
                - <a href="{path}/redoc" target="_blank">ReDoc</a>
            </li>
        """

    html += """
        </ul>

        <h2>🎛️ Controls</h2>
        <button onclick="restart()">🔄 Restart Server</button>
        <button onclick="stop()">🛑 Stop Server</button>
        <button onclick="showLogs()">📊 View Logs</button>

        <div id="logs" style="display:none; margin-top: 20px;">
            <h3>Recent Logs</h3>
            <pre id="log-content" style="background: #f0f0f0; padding: 10px;"></pre>
        </div>

        <script>
            async function restart() {
                if (!confirm('Restart server?')) return;
                await fetch('/admin/restart', {method: 'POST'});
                alert('Server restarting...');
                setTimeout(() => location.reload(), 2000);
            }

            async function stop() {
                if (!confirm('Stop server?')) return;
                await fetch('/admin/stop', {method: 'POST'});
                alert('Server stopped');
            }

            async function showLogs() {
                const logs = document.getElementById('logs');
                if (logs.style.display === 'none') {
                    const response = await fetch('/admin/logs');
                    const text = await response.text();
                    document.getElementById('log-content').textContent = text;
                    logs.style.display = 'block';
                } else {
                    logs.style.display = 'none';
                }
            }
        </script>
    </body>
    </html>
    """

    return html
```

**Admin endpoints:**
```python
@main_app.post("/admin/restart")
async def admin_restart():
    """Trigger server restart."""
    # Signal server to restart
    os.kill(os.getpid(), signal.SIGHUP)
    return {"status": "restarting"}

@main_app.post("/admin/stop")
async def admin_stop():
    """Trigger server stop."""
    os.kill(os.getpid(), signal.SIGTERM)
    return {"status": "stopping"}

@main_app.get("/admin/logs")
async def admin_logs():
    """Get recent logs."""
    with open(".smpub_server.log") as f:
        lines = f.readlines()[-50:]  # Last 50 lines
    return PlainTextResponse("".join(lines))
```

### Usage

```bash
# Start server
smpub serve 8000

# Open dashboard in browser
open http://localhost:8000/

# Dashboard shows:
# - Server status (port, PID, uptime)
# - List of mounted apps with links to docs
# - Buttons to restart/stop server
# - View logs inline
```

## Complete Workflow Example

```bash
# 1. Register apps for HTTP serving
cd ~/projects/shop
smpub add shop --http

cd ~/projects/inventory
smpub add inventory --http --http-path /inv

# 2. Register a Switcher-only library
cd ~/projects/mylib  # Has Switcher but no Publisher
smpub add mylib      # Auto-wrapped!

# 3. Start multi-app server as daemon
smpub serve 8000
# ✓ Server started on port 8000 (PID: 12345)
# ✓ Mounted: /shop, /inv
# ✓ Dashboard: http://localhost:8000/

# 4. Terminal is free - continue working
smpub list
# Local registered apps:
#   shop → /Users/me/projects/shop (http: /shop)
#   inventory → /Users/me/projects/inventory (http: /inv)
#   mylib → /Users/me/projects/mylib

# 5. Test apps via HTTP
curl http://localhost:8000/shop/product/list
curl http://localhost:8000/inv/stock/check

# 6. Use mylib via CLI (auto-wrapped)
smpub mylib command arg1 arg2

# 7. Add new app and restart server
cd ~/projects/newapp
smpub add newapp --http
smpub serve restart
# ✓ Server restarted with newapp mounted at /newapp

# 8. View status and logs
smpub serve status
# Server running on port 8000 (PID: 12346)
# Uptime: 15 minutes
# Mounted: /shop, /inv, /newapp

smpub serve logs
# [Recent server activity...]

# 9. Open dashboard
open http://localhost:8000/
# See all apps, click restart/stop buttons

# 10. Stop when done
smpub serve stop
# ✓ Server stopped
```

## Technical Considerations

### Registry Format

Backward compatible - existing registries work without changes:
- `type` field optional, defaults to `"publisher"`
- `http` and `http_path` fields optional
- Old apps continue to work normally

### PID File Location

- `.smpub_server.pid` in current directory (git-ignored)
- One server per project directory
- Clean shutdown removes PID file
- Stale PID detection (process check)

### Daemon Implementation

- Uses `subprocess.Popen()` with `start_new_session=True`
- Logs to `.smpub_server.log` (git-ignored)
- Graceful shutdown on SIGTERM
- Signal-based restart (SIGHUP)

### Security Notes

- **Local development only** - no authentication
- Dashboard admin endpoints accessible to localhost
- Production deployments should use proper ASGI server with auth

## Future Enhancements

### SmartSwitch Metrics Plugin

Dashboard could display per-method metrics if SmartSwitch adds `MetricsPlugin`:

```python
📊 /shop - Metrics
  - product_list: 145 calls, avg 12ms
  - product_add: 23 calls, avg 45ms, 2 errors
```

This would require:
1. Add `MetricsPlugin` to SmartSwitch
2. Track calls, timing, errors per method
3. Expose metrics via `publisher.get_metrics()`
4. Display in dashboard

### Hot Reload

Watch registry file and reload apps on change (instead of manual restart):

```python
# Watch .published for changes
import watchdog
observer.schedule(reload_handler, path=".", recursive=False)
```

### Global Server

Option to run one global server for all registered apps:

```bash
smpub serve --global 8000
# Mounts all globally-registered apps
```

## Testing Requirements

- Unit tests for auto-wrapping logic
- Integration tests for multi-app mounting
- Process management tests (start/stop/restart)
- Dashboard rendering tests
- Backward compatibility tests (old registries)

## Documentation Requirements

- Update README with new commands
- Add examples for each feature
- Document registry format changes
- Add troubleshooting section for daemon issues
- Update API reference

---

## Implementation Checklist

- [ ] Feature 1: Auto-wrap Switcher classes
  - [ ] Enhance `discover_publisher_class()` to detect Switcher
  - [ ] Add `type` field to registry
  - [ ] Implement auto-wrapping in `load_app()`
  - [ ] Add tests

- [ ] Feature 2: Multi-app HTTP server
  - [ ] Add `--http` and `--http-path` flags to `add` command
  - [ ] Update registry format
  - [ ] Implement `serve()` with app mounting
  - [ ] Add tests

- [ ] Feature 3: Daemon server
  - [ ] Implement daemon mode with subprocess
  - [ ] Add PID file management
  - [ ] Implement `serve stop/restart/status/logs`
  - [ ] Add process management tests

- [ ] Feature 4: Server dashboard
  - [ ] Implement HTML dashboard rendering
  - [ ] Add admin endpoints (restart/stop/logs)
  - [ ] Add JavaScript controls
  - [ ] Add dashboard tests

- [ ] Documentation
  - [ ] Update README
  - [ ] Add usage examples
  - [ ] Update API docs
  - [ ] Add troubleshooting guide

- [ ] Testing
  - [ ] Unit tests for all new functions
  - [ ] Integration tests for complete workflows
  - [ ] Backward compatibility tests

---

**Priority:** High
**Complexity:** Medium
**Breaking Changes:** None (fully backward compatible)
**Dependencies:** None (uses existing FastAPI/uvicorn)
