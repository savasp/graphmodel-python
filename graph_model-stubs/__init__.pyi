# Type stubs for the graph_model package
from typing import Any, Type, TypeVar

from .core import (
    GraphDataModel,
    IEntity,
    IGraph,
    IGraphTransaction,
    INode,
    IRelationship,
)
from .providers import Neo4jGraph

__all__ = [
    "IEntity",
    "IGraph", 
    "GraphDataModel",
    "INode",
    "IRelationship",
    "IGraphTransaction",
    "Neo4jGraph",
]

# Type variables
T = TypeVar('T', bound=IEntity)
TNode = TypeVar('TNode', bound=INode)
TRelationship = TypeVar('TRelationship', bound=IRelationship)

class Node:
    pass

class Relationship:
    pass

def node(label: str) -> Any:
    pass

def relationship(label: str) -> Any:
    pass

def property_field(indexed: bool = False) -> Any:
    pass

class Neo4jGraph:
    def create(self, obj: Any) -> Any:
        pass

    async def create_node(self, node: Any) -> Any:
        pass

    async def create_relationship(self, relationship: Any) -> Any:
        pass
