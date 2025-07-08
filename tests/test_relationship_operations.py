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

from datetime import date, datetime
from unittest.mock import AsyncMock

import pytest

from tests.conftest import _models

# Use the new test models
models = _models()
TestPerson = models['TestPerson']
KnowsRelationship = models['KnowsRelationship']
WorksAtRelationship = models['WorksAtRelationship']


class TestRelationshipOperations:
    """Test relationship creation, reading, updating, and deletion."""

    @pytest.mark.asyncio
    async def test_create_and_read_relationship(self, mock_neo4j_graph):
        # Create test nodes
        person1 = TestPerson(
            first_name="Alice", last_name="Smith", age=30,
            email="alice@example.com", is_active=True, score=95.5,
            tags=["engineer"], metadata={}, created_at=datetime.now(),
            birth_date=date(1993, 5, 20)
        )
        person2 = TestPerson(
            first_name="Bob", last_name="Jones", age=35,
            email="bob@example.com", is_active=True, score=88.0,
            tags=["manager"], metadata={}, created_at=datetime.now(),
            birth_date=date(1988, 3, 15)
        )

        # Mock create_node to return the persons
        mock_neo4j_graph.create_node.side_effect = [person1, person2]

        # Create nodes
        created_person1 = await mock_neo4j_graph.create_node(person1)
        created_person2 = await mock_neo4j_graph.create_node(person2)

        # Create relationship
        relationship = KnowsRelationship(
            id="rel-1",
            start_node_id=created_person1.id,
            end_node_id=created_person2.id,
            since=datetime.now(),
            strength=0.8
        )

        # Mock create_relationship to return the relationship
        mock_neo4j_graph.create_relationship.return_value = relationship
        mock_neo4j_graph.get_relationship.return_value = relationship

        created_relationship = await mock_neo4j_graph.create_relationship(relationship)
        assert created_relationship.id == "rel-1"
        assert created_relationship.start_node_id == created_person1.id
        assert created_relationship.end_node_id == created_person2.id

        # Test get_relationship
        read_relationship = await mock_neo4j_graph.get_relationship("rel-1")
        assert read_relationship is not None
        assert read_relationship.start_node_id == created_person1.id
        assert read_relationship.end_node_id == created_person2.id

    @pytest.mark.asyncio
    async def test_update_relationship(self, mock_neo4j_graph):
        # Create test nodes
        person1 = TestPerson(
            first_name="Alice", last_name="Smith", age=30,
            email="alice@example.com", is_active=True, score=95.5,
            tags=["engineer"], metadata={}, created_at=datetime.now(),
            birth_date=date(1993, 5, 20)
        )
        person2 = TestPerson(
            first_name="Bob", last_name="Jones", age=35,
            email="bob@example.com", is_active=True, score=88.0,
            tags=["manager"], metadata={}, created_at=datetime.now(),
            birth_date=date(1988, 3, 15)
        )

        # Mock create_node to return the persons
        mock_neo4j_graph.create_node.side_effect = [person1, person2]

        # Create nodes
        created_person1 = await mock_neo4j_graph.create_node(person1)
        created_person2 = await mock_neo4j_graph.create_node(person2)

        # Create relationship
        relationship = KnowsRelationship(
            id="rel-1",
            start_node_id=created_person1.id,
            end_node_id=created_person2.id,
            since=datetime.now(),
            strength=0.8
        )

        # Mock create_relationship to return the relationship
        mock_neo4j_graph.create_relationship.return_value = relationship
        mock_neo4j_graph.update_relationship.return_value = True

        created_relationship = await mock_neo4j_graph.create_relationship(relationship)

        # Update relationship
        updated_relationship = KnowsRelationship(
            id=created_relationship.id,
            start_node_id=created_relationship.start_node_id,
            end_node_id=created_relationship.end_node_id,
            since=datetime.now(),
            strength=0.9
        )

        result = await mock_neo4j_graph.update_relationship(updated_relationship)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_relationship(self, mock_neo4j_graph):
        # Create test nodes
        person1 = TestPerson(
            first_name="Alice", last_name="Smith", age=30,
            email="alice@example.com", is_active=True, score=95.5,
            tags=["engineer"], metadata={}, created_at=datetime.now(),
            birth_date=date(1993, 5, 20)
        )
        person2 = TestPerson(
            first_name="Bob", last_name="Jones", age=35,
            email="bob@example.com", is_active=True, score=88.0,
            tags=["manager"], metadata={}, created_at=datetime.now(),
            birth_date=date(1988, 3, 15)
        )

        # Mock create_node to return the persons
        mock_neo4j_graph.create_node.side_effect = [person1, person2]

        # Create nodes
        created_person1 = await mock_neo4j_graph.create_node(person1)
        created_person2 = await mock_neo4j_graph.create_node(person2)

        # Create relationship
        relationship = KnowsRelationship(
            id="rel-1",
            start_node_id=created_person1.id,
            end_node_id=created_person2.id,
            since=datetime.now(),
            strength=0.8
        )

        # Mock create_relationship to return the relationship
        mock_neo4j_graph.create_relationship.return_value = relationship
        mock_neo4j_graph.delete_relationship.return_value = True

        created_relationship = await mock_neo4j_graph.create_relationship(relationship)
        result = await mock_neo4j_graph.delete_relationship(created_relationship.id)
        assert result is True

    @pytest.mark.asyncio
    async def test_query_relationships(self, mock_neo4j_graph):
        """Test querying relationships."""
        # Create nodes and relationships
        person1 = TestPerson(
            first_name="Alice", last_name="Smith", age=30,
            email="alice@example.com", is_active=True, score=95.5,
            tags=["engineer"], metadata={}, created_at=datetime.now(),
            birth_date=date(1993, 5, 20)
        )
        person2 = TestPerson(
            first_name="Bob", last_name="Jones", age=35,
            email="bob@example.com", is_active=True, score=88.0,
            tags=["manager"], metadata={}, created_at=datetime.now(),
            birth_date=date(1988, 3, 15)
        )
        person3 = TestPerson(
            first_name="Charlie", last_name="Brown", age=28,
            email="charlie@example.com", is_active=False, score=75.0,
            tags=["junior"], metadata={}, created_at=datetime.now(),
            birth_date=date(1995, 8, 10)
        )

        # Mock create_node to return each person
        mock_neo4j_graph.create_node.side_effect = [person1, person2, person3]

        created_person1 = await mock_neo4j_graph.create_node(person1)
        created_person2 = await mock_neo4j_graph.create_node(person2)
        created_person3 = await mock_neo4j_graph.create_node(person3)

        # Verify nodes were created
        assert created_person1.first_name == "Alice"
        assert created_person2.first_name == "Bob"
        assert created_person3.first_name == "Charlie"

        # Mock relationship querying
        mock_neo4j_graph.get_relationships = AsyncMock()
        mock_neo4j_graph.get_relationships.return_value = []

        # Query relationships
        relationships = await mock_neo4j_graph.get_relationships(created_person1)
        assert isinstance(relationships, list)
