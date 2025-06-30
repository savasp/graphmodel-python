# Type stubs for the attributes module
from typing import Any, Callable, TypeVar

T = TypeVar('T')

def node(label: str) -> Callable[[type[T]], type[T]]:
    """Decorator to mark a class as a graph node."""
    ...

def relationship(label: str) -> Callable[[type[T]], type[T]]:
    """Decorator to mark a class as a graph relationship."""
    ...

def property_field(
    indexed: bool = False,
    embedded: bool = False,
    related_node: bool = False,
    **kwargs: Any
) -> Any:
    """Create a property field with metadata."""
    ...

def embedded_field(**kwargs: Any) -> Any:
    """Create an embedded field that stores complex objects as properties."""
    ...

def related_node_field(**kwargs: Any) -> Any:
    """Create a related node field that creates relationships to other nodes."""
    ...

__all__ = [
    "node",
    "relationship",
    "property_field",
    "embedded_field",
    "related_node_field",
]
