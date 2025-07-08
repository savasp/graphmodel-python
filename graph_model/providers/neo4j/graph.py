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
Neo4j graph implementation.

This module provides the Neo4j implementation of the graph interface,
using the new type detection system for field processing.
"""

import json
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from neo4j import AsyncGraphDatabase
from neo4j._async.work.transaction import AsyncTransaction

from ...core import FieldStorageType, ModelRegistry, Node, Relationship
from ...core.exceptions import GraphError
from ...core.graph import (
    IGraph,
    IGraphNodeQueryable,
    IGraphRelationshipQueryable,
    IGraphTransaction,
)
from ...core.node import INode
from ...core.relationship import IRelationship
from .cypher_builder import CypherBuilder
from .driver import Neo4jDriver
from .serialization import Neo4jSerializer

TNode = TypeVar('TNode', bound=INode)
TRelationship = TypeVar('TRelationship', bound=IRelationship)


class Neo4jGraph(IGraph[TNode, TRelationship]):
    """Neo4j implementation of the graph interface."""

    def __init__(self, driver: Neo4jDriver):
        """Initialize the Neo4j graph with a driver."""
        self.driver = driver

    async def create_node(self, node: TNode, transaction: Optional[IGraphTransaction] = None) -> TNode:
        """Create a node in the graph."""
        try:
            # Serialize the node using the new system
            # Cast to Node for serialization (assuming TNode extends Node)
            serialized = Neo4jSerializer.serialize_node(node)  # type: ignore
            
            # Use provided transaction or create a new one
            if transaction and hasattr(transaction, '_transaction'):
                tx = transaction._transaction
                session = None
            else:
                session = self.driver.session()
                tx = await session.begin_transaction()

            try:
                # Create the main node
                await self._create_main_node(serialized, tx)
                
                # Create complex properties as separate nodes
                await self._create_complex_properties(node, serialized, tx)
                
                if not transaction and session:
                    await tx.commit()
                    await session.close()
                
                return node
            except Exception as e:
                if not transaction and session:
                    await tx.rollback()
                    await session.close()
                raise e
                
        except Exception as e:
            raise GraphError(f"Failed to create node: {str(e)}") from e

    async def get_node(self, node_id: str, transaction: Optional[IGraphTransaction] = None) -> Optional[TNode]:
        """Get a node by ID."""
        try:
            # Use provided transaction or create a new one
            if transaction and hasattr(transaction, '_transaction'):
                tx = transaction._transaction
                session = None
            else:
                session = self.driver.session()
                tx = await session.begin_transaction()

            try:
                # Simple query to get node
                query = "MATCH (n {id: $node_id}) RETURN n"
                
                result = await tx.run(query, {"node_id": node_id})
                record = await result.single()
                
                if not record:
                    return None
                
                # Deserialize the node using the correct type
                return Neo4jSerializer.deserialize_node(record, self._node_type)  # type: ignore
                
            finally:
                if not transaction and session:
                    await tx.commit()
                    await session.close()
                    
        except Exception as e:
            raise GraphError(f"Failed to get node: {str(e)}") from e

    async def update_node(self, node: TNode, transaction: Optional[IGraphTransaction] = None) -> bool:
        """Update a node in the graph."""
        try:
            # Serialize the node using the new system
            # Cast to Node for serialization (assuming TNode extends Node)
            serialized = Neo4jSerializer.serialize_node(node)  # type: ignore
            
            # Use provided transaction or create a new one
            if transaction and hasattr(transaction, '_transaction'):
                tx = transaction._transaction
                session = None
            else:
                session = self.driver.session()
                tx = await session.begin_transaction()

            try:
                # Update the main node
                await self._update_main_node(serialized, tx)
                
                # Update complex properties
                await self._update_complex_properties(node, serialized, tx)
                
                if not transaction and session:
                    await tx.commit()
                    await session.close()
                
                return True
            except Exception as e:
                if not transaction and session:
                    await tx.rollback()
                    await session.close()
                raise e
                
        except Exception as e:
            raise GraphError(f"Failed to update node: {str(e)}") from e

    async def delete_node(self, node_id: str, transaction: Optional[IGraphTransaction] = None) -> bool:
        """Delete a node from the graph."""
        try:
            # Use provided transaction or create a new one
            if transaction and hasattr(transaction, '_transaction'):
                tx = transaction._transaction
                session = None
            else:
                session = self.driver.session()
                tx = await session.begin_transaction()

            try:
                # Delete complex properties first
                await self._delete_complex_properties(node_id, tx)
                
                # Delete the main node
                query = "MATCH (n {id: $node_id}) DELETE n"
                result = await tx.run(query, {"node_id": node_id})
                
                if not transaction and session:
                    await tx.commit()
                    await session.close()
                
                return True
            except Exception as e:
                if not transaction and session:
                    await tx.rollback()
                    await session.close()
                raise e
                
        except Exception as e:
            raise GraphError(f"Failed to delete node: {str(e)}") from e

    async def create_relationship(self, relationship: TRelationship, transaction: Optional[IGraphTransaction] = None) -> TRelationship:
        """Create a relationship in the graph."""
        try:
            # Serialize the relationship using the new system
            # Cast to Relationship for serialization (assuming TRelationship extends Relationship)
            serialized = Neo4jSerializer.serialize_relationship(relationship)  # type: ignore
            
            # Use provided transaction or create a new one
            if transaction and hasattr(transaction, '_transaction'):
                tx = transaction._transaction
                session = None
            else:
                session = self.driver.session()
                tx = await session.begin_transaction()

            try:
                # Create the relationship
                await self._create_main_relationship(serialized, tx)
                
                if not transaction and session:
                    await tx.commit()
                    await session.close()
                
                return relationship
            except Exception as e:
                if not transaction and session:
                    await tx.rollback()
                    await session.close()
                raise e
                
        except Exception as e:
            raise GraphError(f"Failed to create relationship: {str(e)}") from e

    async def get_relationship(self, relationship_id: str, transaction: Optional[IGraphTransaction] = None) -> Optional[TRelationship]:
        """Get a relationship by ID."""
        try:
            # Use provided transaction or create a new one
            if transaction and hasattr(transaction, '_transaction'):
                tx = transaction._transaction
                session = None
            else:
                session = self.driver.session()
                tx = await session.begin_transaction()

            try:
                query = "MATCH ()-[r {id: $relationship_id}]->() RETURN r"
                result = await tx.run(query, {"relationship_id": relationship_id})
                record = await result.single()

                if not record:
                    return None

                # Use the correct relationship type for deserialization
                rel_type = getattr(self, '_relationship_type', None) or TRelationship
                return Neo4jSerializer.deserialize_relationship(record, rel_type)  # type: ignore

            finally:
                if not transaction and session:
                    await tx.commit()
                    await session.close()

        except Exception as e:
            raise GraphError(f"Failed to get relationship: {str(e)}") from e

    async def update_relationship(self, relationship: TRelationship, transaction: Optional[IGraphTransaction] = None) -> bool:
        """Update a relationship in the graph."""
        try:
            # Serialize the relationship using the new system
            # Cast to Relationship for serialization (assuming TRelationship extends Relationship)
            serialized = Neo4jSerializer.serialize_relationship(relationship)  # type: ignore
            
            # Use provided transaction or create a new one
            if transaction and hasattr(transaction, '_transaction'):
                tx = transaction._transaction
                session = None
            else:
                session = self.driver.session()
                tx = await session.begin_transaction()

            try:
                # Update the main relationship
                await self._update_main_relationship(serialized, tx)
                
                if not transaction and session:
                    await tx.commit()
                    await session.close()
                
                return True
            except Exception as e:
                if not transaction and session:
                    await tx.rollback()
                    await session.close()
                raise e
                
        except Exception as e:
            raise GraphError(f"Failed to update relationship: {str(e)}") from e

    async def delete_relationship(self, relationship_id: str, transaction: Optional[IGraphTransaction] = None) -> bool:
        """Delete a relationship from the graph."""
        try:
            # Use provided transaction or create a new one
            if transaction and hasattr(transaction, '_transaction'):
                tx = transaction._transaction
                session = None
            else:
                session = self.driver.session()
                tx = await session.begin_transaction()

            try:
                query = "MATCH ()-[r {id: $relationship_id}]->() DELETE r"
                result = await tx.run(query, {"relationship_id": relationship_id})
                
                if not transaction and session:
                    await tx.commit()
                    await session.close()
                
                return True
            except Exception as e:
                if not transaction and session:
                    await tx.rollback()
                    await session.close()
                raise e
                
        except Exception as e:
            raise GraphError(f"Failed to delete relationship: {str(e)}") from e

    def transaction(self) -> IGraphTransaction:
        """Create a new transaction."""
        session = self.driver.session()
        return Neo4jTransaction(session)

    def nodes(self, node_type: Type[TNode]) -> IGraphNodeQueryable[TNode]:
        """Get a queryable for nodes of the specified type."""
        # Get node metadata
        metadata = getattr(node_type, '__graph_node_metadata__', None)
        if metadata:
            labels = [metadata['label']]
        else:
            labels = [node_type.__name__]
            
        return Neo4jNodeQueryable(self.driver, node_type, labels)

    def relationships(self, relationship_type: Type[TRelationship]) -> IGraphRelationshipQueryable[TRelationship]:
        """Get a queryable for relationships of the specified type."""
        # Get relationship metadata
        metadata = getattr(relationship_type, '__graph_relationship_metadata__', None)
        if metadata:
            rel_type = metadata['label']
        else:
            rel_type = relationship_type.__name__
            
        return Neo4jRelationshipQueryable(self.driver, relationship_type, rel_type)

    async def _create_main_node(self, serialized: Any, tx: AsyncTransaction) -> None:
        """Create the main node in Neo4j."""
        # Build Cypher query
        labels_str = ":".join(serialized.labels)
        properties_str = ", ".join([f"{k}: ${k}" for k in serialized.properties.keys()])
        
        query = f"""
        CREATE (n:{labels_str} {{id: $id, {properties_str}}})
        RETURN n
        """
        
        # Prepare parameters
        params = {"id": serialized.id, **serialized.properties}
        
        await tx.run(query, params)

    async def _create_complex_properties(self, node: TNode, serialized: Any, tx: AsyncTransaction) -> None:
        """Create complex properties as separate nodes with relationships."""
        for field_name, complex_data in serialized.complex_properties.items():
            value = complex_data['value']
            relationship_type = complex_data['relationship_type']
            is_collection = complex_data.get('is_collection', False)
            
            if is_collection:
                for i, item in enumerate(value):
                    await self._create_single_complex_property(
                        node.id, field_name, item, relationship_type, tx, i
                    )
            else:
                await self._create_single_complex_property(
                    node.id, field_name, value, relationship_type, tx
                )

    async def _create_single_complex_property(self, parent_id: str, field_name: str, value: Any, relationship_type: str, tx: AsyncTransaction, sequence: Optional[int] = None) -> None:
        """Create a single complex property as a separate node."""
        # Create the complex property node
        complex_node_id = f"{parent_id}_{field_name}_{sequence or 0}"
        
        # Serialize the complex value
        if hasattr(value, 'model_dump'):
            properties = value.model_dump()
        else:
            properties = value.__dict__ if hasattr(value, '__dict__') else {}
        
        # Add sequence number for collections
        if sequence is not None:
            properties['SequenceNumber'] = sequence
        
        # Create the complex property node
        properties_str = ", ".join([f"{k}: ${k}" for k in properties.keys()])
        query = f"""
        CREATE (cp:ComplexProperty {{id: $complex_id, {properties_str}}})
        """
        await tx.run(query, {"complex_id": complex_node_id, **properties})
        
        # Create the relationship
        rel_query = f"""
        MATCH (parent {{id: $parent_id}})
        MATCH (cp {{id: $complex_id}})
        CREATE (parent)-[r:{relationship_type}]->(cp)
        """
        await tx.run(rel_query, {"parent_id": parent_id, "complex_id": complex_node_id})

    async def _update_main_node(self, serialized: Any, tx: AsyncTransaction) -> None:
        """Update the main node in Neo4j."""
        # Build Cypher query
        labels_str = ":".join(serialized.labels)
        properties_str = ", ".join([f"n.{k} = ${k}" for k in serialized.properties.keys()])
        
        query = f"""
        MATCH (n:{labels_str} {{id: $id}})
        SET {properties_str}
        RETURN n
        """
        
        # Prepare parameters
        params = {"id": serialized.id, **serialized.properties}
        
        await tx.run(query, params)

    async def _update_complex_properties(self, node: TNode, serialized: Any, tx: AsyncTransaction) -> None:
        """Update complex properties."""
        # For now, we'll delete and recreate complex properties
        # In a more sophisticated implementation, you'd update them in place
        await self._delete_complex_properties(node.id, tx)
        await self._create_complex_properties(node, serialized, tx)

    async def _delete_complex_properties(self, node_id: str, tx: AsyncTransaction) -> None:
        """Delete complex properties for a node."""
        query = """
        MATCH (n {id: $node_id})-[r]->(cp:ComplexProperty)
        WHERE type(r) STARTS WITH '__PROPERTY__'
        DELETE r, cp
        """
        await tx.run(query, {"node_id": node_id})

    async def _create_main_relationship(self, serialized: Any, tx: AsyncTransaction) -> None:
        """Create the main relationship in Neo4j."""
        # Build Cypher query
        properties_str = ", ".join([f"{k}: ${k}" for k in serialized.properties.keys()])
        
        query = f"""
        MATCH (start {{id: $start_id}})
        MATCH (end {{id: $end_id}})
        CREATE (start)-[r:{serialized.type} {{id: $id, {properties_str}}}]->(end)
        RETURN r
        """
        
        # Prepare parameters
        params = {
            "id": serialized.id,
            "start_id": serialized.start_node_id,
            "end_id": serialized.end_node_id,
            **serialized.properties
        }
        
        await tx.run(query, params)

    async def _update_main_relationship(self, serialized: Any, tx: AsyncTransaction) -> None:
        """Update the main relationship in Neo4j."""
        # Build Cypher query
        properties_str = ", ".join([f"r.{k} = ${k}" for k in serialized.properties.keys()])
        
        query = f"""
        MATCH ()-[r:{serialized.type} {{id: $id}}]->()
        SET {properties_str}
        RETURN r
        """
        
        # Prepare parameters
        params = {"id": serialized.id, **serialized.properties}
        
        await tx.run(query, params)


class Neo4jTransaction(IGraphTransaction):
    """Neo4j transaction implementation."""

    def __init__(self, session):
        """Initialize the transaction."""
        self.session = session
        self._transaction = None
        self._is_active = False
        self._is_committed = False
        self._is_rolled_back = False

    @property
    def is_active(self) -> bool:
        """Check if the transaction is currently active."""
        return self._is_active

    @property
    def is_committed(self) -> bool:
        """Check if the transaction has been committed."""
        return self._is_committed

    @property
    def is_rolled_back(self) -> bool:
        """Check if the transaction has been rolled back."""
        return self._is_rolled_back

    async def commit(self) -> None:
        """Commit the transaction."""
        if self._transaction:
            await self._transaction.commit()
            self._is_committed = True
            self._is_active = False

    async def rollback(self) -> None:
        """Roll back the transaction."""
        if self._transaction:
            await self._transaction.rollback()
            self._is_rolled_back = True
            self._is_active = False

    async def close(self) -> None:
        """Close the transaction."""
        if self._transaction:
            await self._transaction.close()
        await self.session.close()
        self._is_active = False

    async def __aenter__(self):
        """Enter the transaction context."""
        self._transaction = await self.session.begin_transaction()
        self._is_active = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit the transaction context."""
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()
        await self.close()


class Neo4jNodeQueryable(IGraphNodeQueryable[TNode]):
    """Neo4j implementation of node queryable."""

    def __init__(self, driver: Neo4jDriver, node_type: Type[TNode], labels: List[str]):
        """Initialize the node queryable."""
        self.driver = driver
        self.node_type = node_type
        self.labels = labels
        self._filters = []
        self._order_by = []
        self._take = None
        self._skip = None

    def where(self, predicate) -> 'Neo4jNodeQueryable[TNode]':
        """Add a filter to the query."""
        self._filters.append(predicate)
        return self

    def order_by(self, key_selector) -> 'Neo4jNodeQueryable[TNode]':
        """Add ordering to the query."""
        self._order_by.append(key_selector)
        return self

    def take(self, count: int) -> 'Neo4jNodeQueryable[TNode]':
        """Limit the number of results."""
        self._take = count
        return self

    def skip(self, count: int) -> 'Neo4jNodeQueryable[TNode]':
        """Skip a number of results."""
        self._skip = count
        return self

    async def to_list(self) -> List[TNode]:
        """Execute the query and return all results."""
        # Build Cypher query
        labels_str = ":".join(self.labels)
        query = f"MATCH (n:{labels_str})"
        
        # Add filters
        if self._filters:
            # For now, we'll use a simple approach
            # In a real implementation, you'd translate predicates to Cypher
            pass
        
        # Add ordering
        if self._order_by:
            # For now, we'll use a simple approach
            # In a real implementation, you'd translate key selectors to Cypher
            pass
        
        # Add pagination
        if self._skip:
            query += f" SKIP {self._skip}"
        if self._take:
            query += f" LIMIT {self._take}"
        
        query += " RETURN n"
        
        # Execute query
        session = self.driver.session()
        try:
            result = await session.run(query)
            records = await result.to_list()
            
            # Deserialize results
            nodes = []
            for record in records:
                node_data = dict(record.get('n', {}))
                node = self.node_type(**node_data)
                nodes.append(node)
            
            return nodes
        finally:
            await session.close()

    async def first_or_default(self) -> Optional[TNode]:
        """Get the first result or None."""
        self._take = 1
        results = await self.to_list()
        return results[0] if results else None

    async def single_or_default(self) -> Optional[TNode]:
        """Get the single result or None."""
        results = await self.to_list()
        if len(results) == 1:
            return results[0]
        elif len(results) == 0:
            return None
        else:
            raise GraphError("More than one result found")


class Neo4jRelationshipQueryable(IGraphRelationshipQueryable[TRelationship]):
    """Neo4j implementation of relationship queryable."""

    def __init__(self, driver: Neo4jDriver, relationship_type: Type[TRelationship], rel_type: str):
        """Initialize the relationship queryable."""
        self.driver = driver
        self.relationship_type = relationship_type
        self.rel_type = rel_type
        self._filters = []
        self._order_by = []
        self._take = None
        self._skip = None

    def where(self, predicate) -> 'Neo4jRelationshipQueryable[TRelationship]':
        """Add a filter to the query."""
        self._filters.append(predicate)
        return self

    def order_by(self, key_selector) -> 'Neo4jRelationshipQueryable[TRelationship]':
        """Add ordering to the query."""
        self._order_by.append(key_selector)
        return self

    def take(self, count: int) -> 'Neo4jRelationshipQueryable[TRelationship]':
        """Limit the number of results."""
        self._take = count
        return self

    def skip(self, count: int) -> 'Neo4jRelationshipQueryable[TRelationship]':
        """Skip a number of results."""
        self._skip = count
        return self

    async def to_list(self) -> List[TRelationship]:
        """Execute the query and return all results."""
        # Build Cypher query
        query = f"MATCH ()-[r:{self.rel_type}]->()"
        
        # Add filters
        if self._filters:
            # For now, we'll use a simple approach
            # In a real implementation, you'd translate predicates to Cypher
            pass
        
        # Add ordering
        if self._order_by:
            # For now, we'll use a simple approach
            # In a real implementation, you'd translate key selectors to Cypher
            pass
        
        # Add pagination
        if self._skip:
            query += f" SKIP {self._skip}"
        if self._take:
            query += f" LIMIT {self._take}"
        
        query += " RETURN r"
        
        # Execute query
        session = self.driver.session()
        try:
            result = await session.run(query)
            records = await result.to_list()
            
            # Deserialize results
            relationships = []
            for record in records:
                rel_data = dict(record.get('r', {}))
                relationship = self.relationship_type(**rel_data)
                relationships.append(relationship)
            
            return relationships
        finally:
            await session.close()

    async def first_or_default(self) -> Optional[TRelationship]:
        """Get the first result or None."""
        self._take = 1
        results = await self.to_list()
        return results[0] if results else None

    async def single_or_default(self) -> Optional[TRelationship]:
        """Get the single result or None."""
        results = await self.to_list()
        if len(results) == 1:
            return results[0]
        elif len(results) == 0:
            return None
        else:
            raise GraphError("More than one result found")
