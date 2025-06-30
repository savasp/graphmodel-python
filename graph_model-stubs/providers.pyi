# Type stubs for the providers module
from typing import Any, Generic, Optional, Type, TypeVar

from ..core.graph import IGraph, IGraphTransaction
from ..core.node import INode
from ..core.relationship import IRelationship

TNode = TypeVar('TNode', bound=INode)
TRelationship = TypeVar('TRelationship', bound=IRelationship)

# Neo4j provider
class Neo4jGraph(IGraph[TNode, TRelationship]):
    """Neo4j implementation of the IGraph interface."""
    
    def __init__(self) -> None: ...
    
    async def create_node(
        self,
        node: TNode,
        transaction: Optional[IGraphTransaction] = None
    ) -> TNode: ...
    
    async def get_node(
        self,
        node_id: str,
        transaction: Optional[IGraphTransaction] = None
    ) -> Optional[TNode]: ...
    
    async def update_node(
        self,
        node: TNode,
        transaction: Optional[IGraphTransaction] = None
    ) -> TNode: ...
    
    async def delete_node(
        self,
        node_id: str,
        transaction: Optional[IGraphTransaction] = None
    ) -> bool: ...
    
    async def create_relationship(
        self,
        relationship: TRelationship,
        transaction: Optional[IGraphTransaction] = None
    ) -> TRelationship: ...
    
    async def get_relationship(
        self,
        relationship_id: str,
        transaction: Optional[IGraphTransaction] = None
    ) -> Optional[TRelationship]: ...
    
    async def update_relationship(
        self,
        relationship: TRelationship,
        transaction: Optional[IGraphTransaction] = None
    ) -> TRelationship: ...
    
    async def delete_relationship(
        self,
        relationship_id: str,
        transaction: Optional[IGraphTransaction] = None
    ) -> bool: ...
    
    def transaction(self) -> IGraphTransaction: ...
    
    def nodes(self, node_type: Type[TNode]) -> Any: ...
    
    def relationships(self, relationship_type: Type[TRelationship]) -> Any: ...

__all__ = [
    "Neo4jGraph",
]
