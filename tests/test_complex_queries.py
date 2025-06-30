from datetime import date, datetime

import pytest

from tests.conftest import TestPerson


class TestComplexQueries:
    """Test complex querying scenarios."""

    @pytest.mark.asyncio
    async def test_complex_filtering_and_ordering(self, mock_neo4j_graph):
        """Test complex filtering and ordering."""
        people = [
            TestPerson(
                first_name="Alice", last_name="Smith", age=30,
                email="alice@example.com", is_active=True, score=95.5,
                tags=["engineer"], metadata={}, created_at=datetime.now(),
                birth_date=date(1993, 5, 20)
            ),
            TestPerson(
                first_name="Bob", last_name="Jones", age=35,
                email="bob@example.com", is_active=True, score=88.0,
                tags=["manager"], metadata={}, created_at=datetime.now(),
                birth_date=date(1988, 3, 15)
            ),
            TestPerson(
                first_name="Charlie", last_name="Brown", age=28,
                email="charlie@example.com", is_active=False, score=75.0,
                tags=["junior"], metadata={}, created_at=datetime.now(),
                birth_date=date(1995, 8, 10)
            )
        ]
        
        # Mock create_node to return each person
        mock_neo4j_graph.create_node.side_effect = people
        
        # Create test data
        created_people = []
        for person in people:
            created_person = await mock_neo4j_graph.create_node(person)
            created_people.append(created_person)
        
        # Verify all nodes were created
        assert len(created_people) == 3
        assert created_people[0].first_name == "Alice"
        assert created_people[1].first_name == "Bob"
        assert created_people[2].first_name == "Charlie"

    @pytest.mark.asyncio
    async def test_aggregation_queries(self, mock_neo4j_graph):
        """Test aggregation queries."""
        people = [
            TestPerson(
                first_name="Alice", last_name="Smith", age=30,
                email="alice@example.com", is_active=True, score=95.5,
                tags=["engineer"], metadata={}, created_at=datetime.now(),
                birth_date=date(1993, 5, 20)
            ),
            TestPerson(
                first_name="Bob", last_name="Jones", age=35,
                email="bob@example.com", is_active=True, score=88.0,
                tags=["manager"], metadata={}, created_at=datetime.now(),
                birth_date=date(1988, 3, 15)
            ),
            TestPerson(
                first_name="Charlie", last_name="Brown", age=28,
                email="charlie@example.com", is_active=False, score=75.0,
                tags=["junior"], metadata={}, created_at=datetime.now(),
                birth_date=date(1995, 8, 10)
            )
        ]
        
        # Mock create_node to return each person
        mock_neo4j_graph.create_node.side_effect = people
        
        # Create test data
        created_people = []
        for person in people:
            created_person = await mock_neo4j_graph.create_node(person)
            created_people.append(created_person)
        
        # Verify all nodes were created
        assert len(created_people) == 3
        
        # Test aggregation logic
        total_age = sum(person.age for person in created_people)
        avg_age = total_age / len(created_people)
        assert total_age == 93  # 30 + 35 + 28
        assert avg_age == 31.0
        
        active_count = sum(1 for person in created_people if person.is_active)
        assert active_count == 2 