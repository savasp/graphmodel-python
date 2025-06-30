# Type stubs for the core module
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar('T', bound='IEntity')
TNode = TypeVar('TNode', bound='INode')
TRelationship = TypeVar('TRelationship', bound='IRelationship')

# Entity interface
class IEntity(ABC):
    """Base interface for all graph entities."""
    id: str

    @abstractmethod
    def __init__(self, **kwargs: Any) -> None: ...

# Node interface
class INode(IEntity):
    """Interface for graph nodes."""
    pass

# Relationship interface
class IRelationship(IEntity):
    """Interface for graph relationships."""
    start_node_id: str
    end_node_id: str
    type: str

# Transaction interface
class IGraphTransaction(ABC):
    """Interface for graph transactions."""

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

# Graph interface
class IGraph(ABC, Generic[TNode, TRelationship]):
    """Core interface for graph database operations."""

    @abstractmethod
    async def create_node(self, node: TNode, transaction: IGraphTransaction | None = None) -> TNode: ...

    @abstractmethod
    async def get_node(self, node_id: str, transaction: IGraphTransaction | None = None) -> TNode | None: ...

    @abstractmethod
    async def update_node(self, node: TNode, transaction: IGraphTransaction | None = None) -> TNode: ...

    @abstractmethod
    async def delete_node(self, node_id: str, transaction: IGraphTransaction | None = None) -> bool: ...

    @abstractmethod
    async def create_relationship(self, relationship: TRelationship, transaction: IGraphTransaction | None = None) -> TRelationship: ...

    @abstractmethod
    async def get_relationship(self, relationship_id: str, transaction: IGraphTransaction | None = None) -> TRelationship | None: ...

    @abstractmethod
    async def update_relationship(self, relationship: TRelationship, transaction: IGraphTransaction | None = None) -> TRelationship: ...

    @abstractmethod
    async def delete_relationship(self, relationship_id: str, transaction: IGraphTransaction | None = None) -> bool: ...

    @abstractmethod
    def transaction(self) -> IGraphTransaction: ...

    @abstractmethod
    def nodes(self, node_type: type[TNode]) -> IGraphNodeQueryable[TNode]: ...

    @abstractmethod
    def relationships(self, relationship_type: type[TRelationship]) -> IGraphRelationshipQueryable[TRelationship]: ...

# Queryable interfaces
class IGraphNodeQueryable(Generic[TNode]):
    """Interface for queryable node collections."""

    @abstractmethod
    def where(self, predicate: Any) -> IGraphNodeQueryable[TNode]: ...

    @abstractmethod
    def order_by(self, key_selector: Any) -> IOrderedGraphNodeQueryable[TNode]: ...

    @abstractmethod
    def take(self, count: int) -> IGraphNodeQueryable[TNode]: ...

    @abstractmethod
    def skip(self, count: int) -> IGraphNodeQueryable[TNode]: ...

    @abstractmethod
    async def to_list(self) -> list[TNode]: ...

    @abstractmethod
    async def first_or_default(self) -> TNode | None: ...

    @abstractmethod
    async def single_or_default(self) -> TNode | None: ...

class IOrderedGraphNodeQueryable(IGraphNodeQueryable[TNode]):
    """Interface for ordered queryable node collections."""

    @abstractmethod
    def then_by(self, key_selector: Any) -> IOrderedGraphNodeQueryable[TNode]: ...

class IGraphRelationshipQueryable(Generic[TRelationship]):
    """Interface for queryable relationship collections."""

    @abstractmethod
    def where(self, predicate: Any) -> IGraphRelationshipQueryable[TRelationship]: ...

    @abstractmethod
    def order_by(self, key_selector: Any) -> IOrderedGraphRelationshipQueryable[TRelationship]: ...

    @abstractmethod
    def take(self, count: int) -> IGraphRelationshipQueryable[TRelationship]: ...

    @abstractmethod
    def skip(self, count: int) -> IGraphRelationshipQueryable[TRelationship]: ...

    @abstractmethod
    async def to_list(self) -> list[TRelationship]: ...

class IOrderedGraphRelationshipQueryable(IGraphRelationshipQueryable[TRelationship]):
    """Interface for ordered queryable relationship collections."""

    @abstractmethod
    def then_by(self, key_selector: Any) -> IOrderedGraphRelationshipQueryable[TRelationship]: ...

# GraphDataModel utility class
class GraphDataModel:
    """Utility class for graph data model operations."""

    DEFAULT_DEPTH_ALLOWED: int
    PROPERTY_RELATIONSHIP_TYPE_NAME_PREFIX: str
    PROPERTY_RELATIONSHIP_TYPE_NAME_SUFFIX: str

    @staticmethod
    def property_name_to_relationship_type_name(property_name: str) -> str: ...

    @staticmethod
    def relationship_type_name_to_property_name(relationship_type_name: str) -> str: ...

    @staticmethod
    def is_valid_relationship_type_name(relationship_type_name: str) -> bool: ...

    @staticmethod
    def is_simple_type(type_hint: type) -> bool: ...

    @staticmethod
    def is_collection_of_simple(type_hint: type) -> bool: ...

    @staticmethod
    def is_complex_type(type_hint: type, depth: int = ...) -> bool: ...

    @staticmethod
    def is_collection_of_complex(type_hint: type) -> bool: ...

    @staticmethod
    def get_simple_properties(obj: Any) -> dict[str, Any]: ...

    @staticmethod
    def get_complex_properties(obj: Any) -> dict[str, Any]: ...

    @staticmethod
    def get_simple_and_complex_properties(obj: Any) -> tuple[dict[str, Any], dict[str, Any]]: ...

__all__ = [
    "IEntity",
    "INode",
    "IRelationship",
    "IGraphTransaction",
    "IGraph",
    "IGraphNodeQueryable",
    "IOrderedGraphNodeQueryable",
    "IGraphRelationshipQueryable",
    "IOrderedGraphRelationshipQueryable",
    "GraphDataModel",
]
