from datetime import date, datetime

import pytest

from graph_model.core.exceptions import GraphError
from tests.conftest import TestPerson


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_create_duplicate_node(self, mock_neo4j_graph, sample_person):
        """Test creating a node with duplicate ID."""
        # Mock the first create_node to succeed
        mock_neo4j_graph.create_node.return_value = sample_person
        
        # Create node
        created_person = await mock_neo4j_graph.create_node(sample_person)
        
        # Try to create another node with the same ID
        duplicate_person = TestPerson(
            id=created_person.id,  # Use the same ID
            first_name="Duplicate", last_name="Person", age=25,
            email="duplicate@example.com", is_active=True, score=50.0,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=date(1998, 1, 1)
        )
        
        # Mock the second create_node to raise an error
        mock_neo4j_graph.create_node.side_effect = GraphError("Node with this ID already exists")
        
        # This should raise an error
        with pytest.raises(GraphError):
            await mock_neo4j_graph.create_node(duplicate_person)

    @pytest.mark.asyncio
    async def test_update_nonexistent_node(self, mock_neo4j_graph):
        """Test updating a node that doesn't exist."""
        person = TestPerson(
            id="nonexistent-id",  # Set ID in constructor
            first_name="Nonexistent", last_name="Person", age=25,
            email="nonexistent@example.com", is_active=True, score=50.0,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=date(1998, 1, 1)
        )
        
        # Mock update_node to raise an error
        mock_neo4j_graph.update_node.side_effect = GraphError("Node not found")
        
        # This should raise an error
        with pytest.raises(GraphError):
            await mock_neo4j_graph.update_node(person)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_node(self, mock_neo4j_graph):
        """Test deleting a node that doesn't exist."""
        person = TestPerson(
            id="nonexistent-id",  # Set ID in constructor
            first_name="Nonexistent", last_name="Person", age=25,
            email="nonexistent@example.com", is_active=True, score=50.0,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=date(1998, 1, 1)
        )
        
        # Mock delete_node to raise an error
        mock_neo4j_graph.delete_node.side_effect = GraphError("Node not found")
        
        # This should raise an error
        with pytest.raises(GraphError):
            await mock_neo4j_graph.delete_node(person) 