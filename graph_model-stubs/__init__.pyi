# Type stubs for the graph_model package
from typing import Any, Type

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