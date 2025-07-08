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

"""
Graph Model - A Python library for modeling graph data with Neo4j.

This library provides a type-safe, annotation-based approach to modeling
graph data structures with automatic serialization and querying capabilities.
"""

from .attributes import Default, Indexed, Required, node, relationship

# Core interfaces and base classes
# Decorators for entity configuration
from .attributes.decorators import node, relationship

# Field types for property configuration
from .attributes.fields import (
    PropertyFieldInfo,
    PropertyFieldType,
    auto_field,
    determine_field_type_from_annotation,
    embedded_field,
    get_field_info,
    get_relationship_type_for_field,
    property_field,
    related_node_field,
)
from .core import (
    FieldInfo,
    FieldStorageType,
    GraphError,
    IEntity,
    IGraph,
    INode,
    IRelationship,
    ModelRegistry,
    Node,
    Relationship,
    RelationshipDirection,
    TypeDetector,
    generate_entity_id,
)
from .core.entity import IEntity
from .core.exceptions import (
    GraphConnectionError,
    GraphQueryError,
    GraphTransactionError,
    GraphValidationError,
)
from .core.graph import GraphDataModel, IGraph
from .core.node import INode, Node
from .core.relationship import IRelationship, Relationship, RelationshipDirection
from .core.transaction import IGraphTransaction
from .providers.neo4j.graph import Neo4jGraph

# Querying interfaces
from .querying.queryable import (
    IGraphNodeQueryable,
    IGraphRelationshipQueryable,
    IOrderedGraphNodeQueryable,
    IOrderedGraphRelationshipQueryable,
)

# Graph traversal
from .querying.traversal import GraphTraversalDirection

# Version information
__version__ = "0.1.0"
__author__ = "Graph Model Team"
__description__ = "A modern Python library for graph databases with .NET compatibility"

# Convenience exports for common use cases
__all__ = [
    # Core entities
    "Node",
    "Relationship",
    "IEntity", 
    "INode",
    "IRelationship",
    
    # Graph operations
    "IGraph",
    "GraphError",
    "RelationshipDirection",
    
    # Decorators
    "node",
    "relationship",
    
    # Annotations
    "Indexed",
    "Required", 
    "Default",
    
    # Type detection system
    "TypeDetector",
    "FieldStorageType",
    "ModelRegistry",
    "FieldInfo",
    
    # Utilities
    "generate_entity_id",

    # Exceptions
    "GraphValidationError",
    "GraphConnectionError",
    "GraphQueryError",
    "GraphTransactionError",

    # Field types
    "property_field",
    "embedded_field",
    "related_node_field",
    "auto_field",
    "PropertyFieldType",
    "PropertyFieldInfo",
    "get_field_info",
    "determine_field_type_from_annotation",
    "get_relationship_type_for_field",

    # Querying
    "IGraphNodeQueryable",
    "IOrderedGraphNodeQueryable",
    "IGraphRelationshipQueryable",
    "IOrderedGraphRelationshipQueryable",
    "GraphTraversalDirection",

    # Neo4j Graph
    "Neo4jGraph",
]
