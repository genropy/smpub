"""
Channel Registry - Autodiscovery and management of channels.

Channels are transport layers (CLI, HTTP, WebSocket, etc.) that expose
the business logic of apps.
"""

from smartroute.core import Router, RoutedClass, route


class ChanRegistry(RoutedClass):
    """
    Registry for managing channels.

    Autodiscovers available channels and creates instances.
    """

    api = Router(name="chan").plug("pydantic")

    def __init__(self, publisher):
        """
        Initialize registry, autodiscover and create channels.

        Args:
            publisher: Publisher instance to pass to channels
        """
        self._publisher = publisher
        self._channel_classes = {}
        self._channels = {}
        self._autodiscover()
        self._create_channels()

    def _autodiscover(self):
        """
        Autodiscover available channels.

        Attempts to import each channel and registers it if available.
        Gracefully handles missing dependencies.
        """
        # Try to discover CLI channel
        try:
            from .channels.cli_channel import CLIChannel
            self.register('cli', CLIChannel)
        except ImportError:
            pass  # CLI channel not available

        # Try to discover HTTP channel
        try:
            from .channels.http_channel import PublisherHTTP
            self.register('http', PublisherHTTP)
        except ImportError:
            pass  # HTTP channel not available (maybe FastAPI not installed)

    def register(self, name: str, channel_class):
        """
        Register a channel class.

        Args:
            name: Channel identifier (e.g., 'cli', 'http')
            channel_class: Channel class (not instance)
        """
        self._channel_classes[name] = channel_class

    def unregister(self, name: str):
        """
        Unregister a channel.

        Args:
            name: Channel identifier
        """
        if name in self._channel_classes:
            del self._channel_classes[name]

    def _create_channels(self):
        """Create instances of all registered channels."""
        self._channels = {
            name: channel_class(self._publisher)
            for name, channel_class in self._channel_classes.items()
        }

    @route("api")
    def get_available_channels(self) -> dict:
        """
        Get list of available channel names.

        Returns:
            dict: Channel information
        """
        return {
            "total": len(self._channels),
            "channels": list(self._channels.keys())
        }

    def get(self, name: str):
        """
        Get a channel instance by name.

        Args:
            name: Channel identifier ('cli', 'http', etc.)

        Returns:
            Channel instance

        Raises:
            KeyError: If channel not found
        """
        if name not in self._channels:
            raise KeyError(f"Channel '{name}' not available. Available: {self.get_available_channels()}")

        return self._channels[name]

    @property
    def channels(self) -> dict:
        """
        Get all channel instances.

        Returns:
            dict: {channel_name: channel_instance}
        """
        return self._channels
