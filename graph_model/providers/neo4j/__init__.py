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
Neo4j provider for the Python Graph Model library.

This package provides a complete Neo4j implementation of the graph model,
including async driver management, CRUD operations, query translation,
and .NET-compatible serialization.
"""

from .aggregation_executor import Neo4jAggregationExecutor, Neo4jGroupByQueryable
from .async_queryable import Neo4jAsyncNodeQueryable, Neo4jAsyncProjectionQueryable
from .cypher_builder import CypherBuilder, CypherQuery, RelationshipCypherBuilder
from .driver import Neo4jDriver
from .graph import Neo4jGraph
from .node_queryable import Neo4jNodeQueryable
from .relationship_queryable import Neo4jRelationshipQueryable
from .serialization import Neo4jSerializer, SerializedNode, SerializedRelationship
from .transaction import Neo4jTransaction
from .traversal_executor import Neo4jTraversalExecutor

__all__ = [
    "Neo4jDriver",
    "Neo4jTransaction", 
    "Neo4jSerializer",
    "SerializedNode",
    "SerializedRelationship",
    "Neo4jGraph",
    "Neo4jNodeQueryable",
    "Neo4jRelationshipQueryable",
    "CypherBuilder",
    "RelationshipCypherBuilder",
    "CypherQuery",
    "Neo4jTraversalExecutor",
    "Neo4jAsyncNodeQueryable",
    "Neo4jAsyncProjectionQueryable",
    "Neo4jAggregationExecutor",
    "Neo4jGroupByQueryable"
] 