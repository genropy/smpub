"""
ApiSwitcher - Switcher with Pydantic model generation for CLI/HTTP.

This module extends smartswitch.Switcher to automatically create Pydantic
models for decorated methods, enabling seamless FastAPI integration.
"""

from enum import Enum
from typing import Any, Optional

from smartswitch import Switcher

try:
    from pydantic import create_model, Field
except ImportError:
    create_model = None
    Field = None

from .validation import get_parameter_info, parse_docstring_params


class ApiSwitcher(Switcher):
    """
    Switcher that automatically creates Pydantic models for decorated methods.

    This class extends smartswitch.Switcher to generate Pydantic models at
    decoration time, making them available for FastAPI OpenAPI schema generation.

    Usage:
        class MyHandler(PublishedClass):
            api = ApiSwitcher(prefix='my_')

            @api
            def my_method(self, name: str, age: int = 25):
                '''Method with parameters.

                Args:
                    name: User's name
                    age: User's age
                '''
                pass

    The generated Pydantic models are stored internally and can be retrieved
    via get_pydantic_model(method_name).
    """

    def __init__(self, prefix: str = ""):
        """
        Initialize ApiSwitcher.

        Args:
            prefix: Method prefix for switcher rules
        """
        super().__init__(prefix=prefix)
        self._pydantic_models: dict[str, Any] = {}

    def __call__(self, func):
        """
        Decorate method and create Pydantic model.

        Args:
            func: Function to decorate

        Returns:
            Decorated function
        """
        # Call parent to register method
        decorated = super().__call__(func)

        # Create Pydantic model for this method
        if create_model is not None:
            model = self._create_pydantic_model(func)
            if model is not None:
                self._pydantic_models[func.__name__] = model

        return decorated

    def _create_pydantic_model(self, func) -> Optional[Any]:
        """
        Create Pydantic model from function signature.

        Args:
            func: Function to analyze

        Returns:
            Pydantic model class or None if no parameters
        """
        # Get parameter info
        params = get_parameter_info(func)
        if not params:
            return None

        # Parse docstring for descriptions
        docstring = func.__doc__ or ""
        param_descriptions = parse_docstring_params(docstring)

        # Build field definitions
        fields = {}
        for param in params:
            param_name = param["name"]
            param_type_str = param["type"]
            default_value = param["default"]
            required = param["required"]
            description = param_descriptions.get(param_name, "")

            # Convert type string to Python type
            python_type = self._convert_type(param_type_str, func.__name__, param_name)

            # Build field definition
            if required:
                # Required field
                if description:
                    fields[param_name] = (python_type, Field(..., description=description))
                else:
                    fields[param_name] = (python_type, ...)
            else:
                # Optional field with default
                if isinstance(python_type, type) and issubclass(python_type, Enum):
                    # Convert default string to enum value
                    default_enum = self._get_enum_default(python_type, default_value)
                    if description:
                        fields[param_name] = (
                            python_type,
                            Field(default=default_enum, description=description),
                        )
                    else:
                        fields[param_name] = (python_type, default_enum)
                else:
                    # Regular type with default
                    if description:
                        fields[param_name] = (
                            python_type,
                            Field(default=default_value, description=description),
                        )
                    else:
                        fields[param_name] = (python_type, default_value)

        # Create model with stable name based on function qualname
        model_name = f"{func.__qualname__.replace('.', '_')}_Request"
        return create_model(model_name, **fields)

    def _convert_type(self, type_str: str, func_name: str, param_name: str) -> type:
        """
        Convert type string to Python type.

        Args:
            type_str: Type as string (e.g., "str", "int", "Literal['a', 'b']")
            func_name: Function name (for enum naming)
            param_name: Parameter name (for enum naming)

        Returns:
            Python type
        """
        if type_str == "str":
            return str
        elif type_str == "int":
            return int
        elif type_str == "float":
            return float
        elif type_str == "bool":
            return bool
        elif type_str.startswith("Literal["):
            # Create Enum for Literal types
            literal_str = type_str[8:-1]  # Remove "Literal[" and "]"
            choices = [choice.strip().strip("'\"") for choice in literal_str.split(",")]

            # Create stable enum name
            enum_name = f"{func_name}_{param_name}_Enum"
            return Enum(enum_name, {choice: choice for choice in choices})
        else:
            # Default to str for unknown types
            return str

    def _get_enum_default(self, enum_type: type[Enum], default_value: Any) -> Any:
        """
        Get enum member from default value string.

        Args:
            enum_type: Enum type
            default_value: Default value (string)

        Returns:
            Enum member matching the value, or first member as fallback
        """
        for member in enum_type:
            if member.value == default_value:
                return member
        # Fallback to first member
        return list(enum_type)[0]

    def get_pydantic_model(self, method_name: str) -> Optional[Any]:
        """
        Get Pydantic model for a method.

        Args:
            method_name: Name of the method

        Returns:
            Pydantic model class or None if not found
        """
        return self._pydantic_models.get(method_name)
