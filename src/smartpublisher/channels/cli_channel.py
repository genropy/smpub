"""
CLIChannel - CLI channel implementation.

Key principle: Use ONLY SmartSwitch APIs!
- switcher.describe() → auto-generated help
- switcher.get(method) → callable (handles validation)
- NO custom parsing, NO inspect, NO validation
- SmartSwitch does EVERYTHING
"""

import sys
from smartroute.core import Router, route, RoutedClass

# Try relative import first (when used as package)
# Fall back to absolute import (when run directly)
try:
    from ..output_formatter import OutputFormatter
except ImportError:
    import os
    import sys
    # Add parent directory to path
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from output_formatter import OutputFormatter


class CLIChannel(RoutedClass):
    """
    CLI channel for Publisher.

    Uses ONLY SmartSwitch APIs - no custom code.
    SmartSwitch handles: validation, introspection, execution.
    """

    # CLI-specific utility commands
    cli_api = Router(name="cli")

    def __init__(self, publisher):
        """Initialize CLI channel."""
        self.publisher = publisher
        self.formatter = OutputFormatter()

    @route("cli_api")
    def help(self, handler_name: str = None) -> dict:
        """
        Show help - auto-generated from SmartSwitch.

        Args:
            handler_name: Optional handler name

        Returns:
            dict: Help data from switcher.describe()
        """
        if handler_name:
            # Get help for specific handler
            if handler_name in self.publisher.published_instances:
                instance = self.publisher.published_instances[handler_name]
                if hasattr(instance.__class__, 'api'):
                    # SmartSwitch provides complete schema
                    return instance.__class__.api.describe()
                return {"error": f"Handler '{handler_name}' has no API"}
            return {"error": f"Handler '{handler_name}' not found"}

        # General help - use SmartSwitch API
        return self.publisher.api.describe()

    @route("cli_api")
    def version(self) -> dict:
        """Show version information."""
        return {
            "app": self.publisher.__class__.__name__,
            "smartpublisher": "0.3.0",
            "smartswitch": "0.11.0"
        }

    def run(self, args: list = None):
        """
        Run CLI - orchestrates command dispatch to specialized handlers.

        Args:
            args: Command line arguments (defaults to sys.argv[1:])
        """
        if args is None:
            args = sys.argv[1:]

        # Show help cases
        if not args or args[0] in ['--help', '-h']:
            self._show_general_help()
            return

        if len(args) == 1:
            self._show_handler_help(args[0])
            return

        # Parse and route
        handler_name = args[0]
        method_name = args[1] if len(args) > 1 else None
        method_args = args[2:]

        if handler_name == '_system':
            self._handle_system_command(method_name, method_args)
        else:
            self._handle_business_command(handler_name, method_name, method_args)

    def _show_general_help(self):
        """Show general help from Publisher API."""
        schema = self.publisher.api.describe()
        output = self.formatter.format_help(schema)
        print(output)

    def _show_handler_help(self, handler_name: str):
        """Show help for specific handler."""
        if handler_name in self.publisher.published_instances:
            instance = self.publisher.published_instances[handler_name]
            if hasattr(instance.__class__, 'api'):
                schema = instance.__class__.api.describe()
                output = self.formatter.format_help(schema)
                print(output)
                return

        # Handler not found or no API - delegate to business command handler
        self._handle_business_command(handler_name, None, [])

    def _handle_system_command(self, method_name: str, method_args: list):
        """
        Handle _system commands.

        Args:
            method_name: System command to execute (None = show help)
            method_args: Arguments for the command
        """
        if not method_name:
            # Show system commands help
            schema = self.publisher.api['_system'].__class__.api.describe()
            output = self.formatter.format_help(schema)
            print(output)
            return

        # Execute system command - SmartSwitch handles everything
        try:
            system_handler = self.publisher.published_instances['_system']
            method_callable = system_handler.__class__.api.get(method_name, use_smartasync=True)
            result = method_callable(system_handler)
            output = self.formatter.format_json(result)
            print(output)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    def _handle_business_command(self, handler_name: str, method_name: str, method_args: list):
        """
        Handle business logic commands.

        Args:
            handler_name: Name of the handler to invoke
            method_name: Method to execute (None = show help)
            method_args: Arguments for the method
        """
        # Check handler exists
        if handler_name not in self.publisher.published_instances:
            print(f"Error: Handler '{handler_name}' not found")
            print(f"Available: {', '.join(self.publisher.published_instances.keys())}")
            return

        instance = self.publisher.published_instances[handler_name]

        # Check has API
        if not hasattr(instance.__class__, 'api'):
            print(f"Error: Handler '{handler_name}' has no API")
            return

        # No method: show handler help
        if not method_name:
            schema = instance.__class__.api.describe()
            output = self.formatter.format_help(schema)
            print(output)
            return

        # Execute method - SmartSwitch handles EVERYTHING
        try:
            method_callable = instance.__class__.api.get(method_name, use_smartasync=True)
            result = method_callable(instance)
            output = self.formatter.format_json(result)
            print(output)

        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
