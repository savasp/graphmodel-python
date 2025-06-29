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

"""Core interfaces and base classes for the graph model."""

from .entity import IEntity
from .exceptions import GraphException, GraphValidationException
from .graph import IGraph
from .node import INode, Node
from .relationship import IRelationship, Relationship, RelationshipDirection
from .transaction import IGraphTransaction

__all__ = [
    "IEntity",
    "INode",
    "Node", 
    "IRelationship",
    "Relationship",
    "RelationshipDirection",
    "IGraph",
    "IGraphTransaction",
    "GraphException",
    "GraphValidationException",
] 