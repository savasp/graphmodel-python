# Copyright 2025 Savas Parastatidis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Decorators for configuring graph model entities."""

from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from ..core.node import Node
from ..core.relationship import Relationship, RelationshipDirection

T = TypeVar("T")

# Registry to store metadata about decorated classes
_NODE_METADATA: Dict[Type, Dict[str, Any]] = {}
_RELATIONSHIP_METADATA: Dict[Type, Dict[str, Any]] = {}


def node(
    label: Optional[str] = None,
    *,
    indexed_properties: Optional[List[str]] = None
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to mark a class as a graph node and configure its metadata.

    Args:
        label: Custom label for the node in the graph. If None, uses the class name.
        indexed_properties: List of properties that should be indexed for performance.

    Returns:
        The decorated class with node metadata attached.

    Example:
        ```python
        @node(label="Person", indexed_properties=["email"])
        @dataclass
        class Person(Node):
            first_name: str
            last_name: str
            email: str
        ```
    """
    def decorator(cls: Type[T]) -> Type[T]:
        if not issubclass(cls, Node):
            raise TypeError(f"Class {cls.__name__} must inherit from Node")
        # Store node metadata
        metadata = {
            "label": label or cls.__name__,
            "indexed_properties": indexed_properties or [],
            "is_node": True,
        }
        _NODE_METADATA[cls] = metadata

        # Add metadata as class attribute for runtime access
        cls.__graph_node_metadata__ = metadata

        return cls

    return decorator


def relationship(
    label: Optional[str] = None,
    *,
    direction: RelationshipDirection = RelationshipDirection.OUTGOING,
    indexed_properties: Optional[List[str]] = None
) -> Callable[[Type[T]], Type[T]]:
    """
    Decorator to mark a class as a graph relationship and configure its metadata.

    Args:
        label: Custom label for the relationship in the graph. If None, uses the class name.
        direction: Default direction for this relationship type.
        indexed_properties: List of properties that should be indexed for performance.

    Returns:
        The decorated class with relationship metadata attached.

    Example:
        ```python
        @relationship(label="KNOWS", direction=RelationshipDirection.BIDIRECTIONAL)
        @dataclass
        class Knows(Relationship):
            since: datetime
            strength: float
        ```
    """
    def decorator(cls: Type[T]) -> Type[T]:
        if not issubclass(cls, Relationship):
            raise TypeError(f"Class {cls.__name__} must inherit from Relationship")
        # Store relationship metadata
        metadata = {
            "label": label or cls.__name__,
            "direction": direction,
            "indexed_properties": indexed_properties or [],
            "is_relationship": True,
        }
        _RELATIONSHIP_METADATA[cls] = metadata

        # Add metadata as class attribute for runtime access
        cls.__graph_relationship_metadata__ = metadata

        return cls

    return decorator


def get_node_metadata(cls: Type) -> Optional[dict[str, Any]]:
    """
    Get the node metadata for a class.

    Args:
        cls: The class to get metadata for.

    Returns:
        The node metadata dictionary, or None if the class is not a node.
    """
    return _NODE_METADATA.get(cls)


def get_relationship_metadata(cls: Type) -> Optional[dict[str, Any]]:
    """
    Get the relationship metadata for a class.

    Args:
        cls: The class to get metadata for.

    Returns:
        The relationship metadata dictionary, or None if the class is not a relationship.
    """
    return _RELATIONSHIP_METADATA.get(cls)


def is_node_type(cls: Type) -> bool:
    """
    Check if a class is decorated as a node.

    Args:
        cls: The class to check.

    Returns:
        True if the class is decorated as a node, False otherwise.
    """
    return cls in _NODE_METADATA


def is_relationship_type(cls: Type) -> bool:
    """
    Check if a class is decorated as a relationship.

    Args:
        cls: The class to check.

    Returns:
        True if the class is decorated as a relationship, False otherwise.
    """
    return cls in _RELATIONSHIP_METADATA


def get_node_label(cls: Type) -> str:
    """
    Get the graph label for a node class.

    Args:
        cls: The node class.

    Returns:
        The graph label for the node.

    Raises:
        ValueError: If the class is not a decorated node.
    """
    metadata = get_node_metadata(cls)
    if metadata is None:
        raise ValueError(f"Class {cls.__name__} is not decorated as a node")
    return metadata["label"]


def get_relationship_label(cls: Type) -> str:
    """
    Get the graph label for a relationship class.

    Args:
        cls: The relationship class.

    Returns:
        The graph label for the relationship.

    Raises:
        ValueError: If the class is not a decorated relationship.
    """
    metadata = get_relationship_metadata(cls)
    if metadata is None:
        raise ValueError(f"Class {cls.__name__} is not decorated as a relationship")
    return metadata["label"]


def get_relationship_direction(cls: Type) -> RelationshipDirection:
    """
    Get the default direction for a relationship class.

    Args:
        cls: The relationship class.

    Returns:
        The default direction for the relationship.

    Raises:
        ValueError: If the class is not a decorated relationship.
    """
    metadata = get_relationship_metadata(cls)
    if metadata is None:
        raise ValueError(f"Class {cls.__name__} is not decorated as a relationship")
    return metadata["direction"]
