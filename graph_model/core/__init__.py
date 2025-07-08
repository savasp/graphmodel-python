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

"""Core graph model functionality."""

from .entity import IEntity, generate_entity_id
from .exceptions import GraphError
from .graph import (
    IGraph,
    IGraphNodeQueryable,
    IGraphRelationshipQueryable,
    IGraphTransaction,
)
from .model_registry import FieldInfo, ModelRegistry
from .node import INode, Node
from .relationship import IRelationship, Relationship, RelationshipDirection
from .transaction import IGraphTransaction
from .type_detection import FieldStorageType, TypeDetector

__all__ = [
    # Entity interfaces
    "IEntity",
    "INode", 
    "IRelationship",
    
    # Base implementations
    "Node",
    "Relationship",
    
    # Graph interfaces
    "IGraph",
    "IGraphNodeQueryable",
    "IGraphRelationshipQueryable", 
    "IGraphTransaction",
    
    # Enums
    "RelationshipDirection",
    
    # Utilities
    "generate_entity_id",
    "GraphError",
    
    # New type detection system
    "TypeDetector",
    "FieldStorageType",
    "ModelRegistry",
    "FieldInfo",
]
