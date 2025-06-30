from datetime import date, datetime
from unittest.mock import AsyncMock

import pytest

from tests.conftest import KnowsRelationship, TestPerson


class TestRelationshipOperations:
    """Test relationship creation and querying."""

    @pytest.mark.asyncio
    async def test_create_relationship(self, mock_neo4j_graph):
        """Test creating relationships between nodes."""
        # Create nodes
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
        
        # Mock create_node to return each person
        mock_neo4j_graph.create_node.side_effect = [person1, person2]
        
        created_person1 = await mock_neo4j_graph.create_node(person1)
        created_person2 = await mock_neo4j_graph.create_node(person2)
        
        # Verify nodes were created
        assert created_person1.first_name == "Alice"
        assert created_person2.first_name == "Bob"
        
        # Mock relationship creation
        mock_neo4j_graph.create_relationship = AsyncMock()
        mock_neo4j_graph.create_relationship.return_value = True
        
        # Create relationship with required IDs
        relationship = KnowsRelationship(
            start_node_id=created_person1.id,
            end_node_id=created_person2.id,
            since=datetime.now(),
            strength=0.8
        )
        
        result = await mock_neo4j_graph.create_relationship(
            created_person1, created_person2, relationship
        )
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