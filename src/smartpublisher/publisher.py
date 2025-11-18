"""
Publisher - Central coordinator for SmartPublisher system.

This is the ONE instance that manages:
- App registry (AppRegistry)
- Channels (CLI, HTTP, etc.)
- Published apps coordination

User apps inherit from PublishedClass, not Publisher.
"""

import sys
from pathlib import Path

# Try relative imports first (when used as package)
# Fall back to absolute imports (when run directly)
try:
    from smartroute import Router, route
    from smartseeds.decorators import smartsuper
    from .published import PublishedClass
    from .app_registry import AppRegistry
    from .chan_registry import ChanRegistry
except ImportError:
    from smartroute import Router, route
    from smartseeds.decorators import smartsuper
    from published import PublishedClass
    from app_registry import AppRegistry
    from chan_registry import ChanRegistry


class Publisher(PublishedClass):
    """
    Central Publisher coordinator.

    This is a singleton-like class that manages the entire system:
    - Registry of apps
    - Multiple channels (CLI, HTTP, etc.)
    - Coordination between apps and channels

    There is ONE Publisher per process.
    Apps inherit from PublishedClass, not Publisher.
    """

    # SmartRoute Router for Publisher commands
    api = Router(name='publisher').plug("logging").plug("pydantic")

    @smartsuper
    def __init__(self, registry_path: Path = None, use_global: bool = False):
        """
        Initialize Publisher.

        Args:
            registry_path: Custom registry path (optional)
            use_global: Use global registry instead of local
        """
        self.app_registry = AppRegistry(self, registry_path=registry_path, use_global=use_global)
        self.chan_registry = ChanRegistry(self)

        # Connect registries via add_child for hierarchical routing
        self.api.add_child(self.app_registry, name="apps")
        self.api.add_child(self.chan_registry, name="chan")

    @route("api")
    def serve(self, channel: str = "http", **options):
        """
        Placeholder serve command exposed via API.

        Args:
            channel: Channel identifier to activate
            **options: Additional channel-specific options
        """
        return {
            "status": "disabled",
            "message": "Serve command not wired yet",
            "channel": channel,
            "options": options,
        }

    @route("api")
    def quit(self):
        """Placeholder quit command exposed via API."""
        return {
            "status": "disabled",
            "message": "Quit command not wired yet",
        }

    def run_cli(self):
        """CLI entry point - delegates to CLI channel."""
        self.chan_registry['cli'].run(sys.argv[1:])

    # @route("api")
    # def load_app(self, app_name: str):
    #     return self.app_registry.load(app_name)

    # @route("api")
    # def unload_app(self, app_name: str):
    #     return self.app_registry.unload(app_name)

    # def get_channel(self, channel_name: str):
    #     return self.chan_registry.get(channel_name)

    # def run_cli(self, args: list = None):
    #     self.chan_registry.get('cli').run(args)

    # def run_http(self, port: int = 8000, **kwargs):
    #     self.chan_registry.get('http').run(port=port, **kwargs)


# # Singleton instance for convenience
# _default_publisher = None


# def get_publisher(use_global: bool = False) -> Publisher:
#     """
#     Get the default Publisher instance.

#     Args:
#         use_global: Use global registry

#     Returns:
#         Publisher instance
#     """
#     global _default_publisher

#     if _default_publisher is None:
#         _default_publisher = Publisher(use_global=use_global)

#     return _default_publisher


# Module-level entry point for CLI
def main():
    """Entry point for smpub command."""
    publisher = Publisher()
    publisher.run_cli()


if __name__ == "__main__":
    main()
