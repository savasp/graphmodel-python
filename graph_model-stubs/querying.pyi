# Type stubs for the querying module
from typing import Any, AsyncIterator, TypeVar

from ..core.graph import IGraphNodeQueryable, IGraphRelationshipQueryable
from ..core.node import INode
from ..core.relationship import IRelationship

TNode = TypeVar('TNode', bound=INode)
TRelationship = TypeVar('TRelationship', bound=IRelationship)

# Queryable implementations
class NodeQueryable(IGraphNodeQueryable[TNode]):
    """Queryable implementation for nodes."""

    def __init__(self, node_type: type[TNode], session: Any) -> None: ...

    def where(self, predicate: Any) -> NodeQueryable[TNode]: ...

    def order_by(self, key_selector: Any) -> OrderedNodeQueryable[TNode]: ...

    def take(self, count: int) -> NodeQueryable[TNode]: ...

    def skip(self, count: int) -> NodeQueryable[TNode]: ...

    async def to_list(self) -> list[TNode]: ...

    async def first_or_default(self) -> TNode | None: ...

    async def single_or_default(self) -> TNode | None: ...

class OrderedNodeQueryable(NodeQueryable[TNode]):
    """Ordered queryable implementation for nodes."""

    def then_by(self, key_selector: Any) -> OrderedNodeQueryable[TNode]: ...

class RelationshipQueryable(IGraphRelationshipQueryable[TRelationship]):
    """Queryable implementation for relationships."""

    def __init__(self, relationship_type: type[TRelationship], session: Any) -> None: ...

    def where(self, predicate: Any) -> RelationshipQueryable[TRelationship]: ...

    def order_by(self, key_selector: Any) -> OrderedRelationshipQueryable[TRelationship]: ...

    def take(self, count: int) -> RelationshipQueryable[TRelationship]: ...

    def skip(self, count: int) -> RelationshipQueryable[TRelationship]: ...

    async def to_list(self) -> list[TRelationship]: ...

class OrderedRelationshipQueryable(RelationshipQueryable[TRelationship]):
    """Ordered queryable implementation for relationships."""

    def then_by(self, key_selector: Any) -> OrderedRelationshipQueryable[TRelationship]: ...

# Traversal functionality
class TraversalExecutor:
    """Executor for graph traversal operations."""

    def __init__(self, session: Any, serializer: Any) -> None: ...

    async def traverse(self, query: Any) -> AsyncIterator[Any]: ...

# Aggregation functionality
class AggregationExecutor:
    """Executor for aggregation operations."""

    def __init__(self, session: Any, serializer: Any) -> None: ...

    async def aggregate(self, query: Any) -> dict[str, Any]: ...

__all__ = [
    "NodeQueryable",
    "OrderedNodeQueryable",
    "RelationshipQueryable",
    "OrderedRelationshipQueryable",
    "TraversalExecutor",
    "AggregationExecutor",
]
