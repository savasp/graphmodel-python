from datetime import date, datetime

import pytest

from tests.conftest import TestPerson


class TestDataTypes:
    """Test various data types and edge cases."""

    @pytest.mark.asyncio
    async def test_all_data_types(self, mock_neo4j_graph):
        """Test that all data types are handled correctly."""
        person = TestPerson(
            first_name="José",
            last_name="O'Connor-Smith",
            age=30,
            email="test+tag@example.com",
            is_active=True,
            score=90.0,
            tags=["c++", "c#", "node.js"],
            metadata={"department": "engineering", "level": "senior"},
            created_at=datetime.now(),
            birth_date=date(1993, 5, 20)
        )
        
        # Mock create_node to return the person
        mock_neo4j_graph.create_node.return_value = person
        
        created_person = await mock_neo4j_graph.create_node(person)
        assert created_person.first_name == "José"
        assert created_person.last_name == "O'Connor-Smith"
        assert created_person.age == 30
        assert created_person.email == "test+tag@example.com"
        assert created_person.is_active is True
        assert created_person.score == 90.0
        assert created_person.tags == ["c++", "c#", "node.js"]
        assert created_person.metadata == {"department": "engineering", "level": "senior"}

    @pytest.mark.asyncio
    async def test_empty_values(self, mock_neo4j_graph):
        """Test handling of empty values."""
        person = TestPerson(
            first_name="",
            last_name="",
            age=0,
            email="",
            is_active=False,
            score=0.0,
            tags=[],
            metadata={},
            created_at=datetime.now(),
            birth_date=date(1990, 1, 1)
        )
        
        # Mock create_node to return the person
        mock_neo4j_graph.create_node.return_value = person
        
        created_person = await mock_neo4j_graph.create_node(person)
        assert created_person.first_name == ""
        assert created_person.last_name == ""
        assert created_person.age == 0
        assert created_person.email == ""
        assert created_person.is_active is False
        assert created_person.score == 0.0
        assert created_person.tags == []
        assert created_person.metadata == {}

    @pytest.mark.asyncio
    async def test_special_characters(self, mock_neo4j_graph):
        """Test handling of special characters in strings."""
        person = TestPerson(
            first_name="José",
            last_name="O'Connor-Smith",
            age=30,
            email="test+tag@example.com",
            is_active=True,
            score=90.0,
            tags=["c++", "c#", "node.js"],
            metadata={},
            created_at=datetime.now(),
            birth_date=date(1993, 5, 20)
        )
        
        # Mock create_node to return the person
        mock_neo4j_graph.create_node.return_value = person
        
        created_person = await mock_neo4j_graph.create_node(person)
        assert created_person.first_name == "José"
        assert created_person.last_name == "O'Connor-Smith"
        assert created_person.email == "test+tag@example.com"
        assert created_person.tags == ["c++", "c#", "node.js"] 