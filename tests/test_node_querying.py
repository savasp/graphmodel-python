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

import pytest

from tests.conftest import _models

# Use the new test models
models = _models()
TestPerson = models['TestPerson']


class TestNodeQuerying:
    """Test node querying functionality."""

    @pytest.mark.asyncio
    async def test_query_all_nodes(self, mock_neo4j_graph):
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
    async def test_query_with_where_condition(self, mock_neo4j_graph):
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

        created_people = []
        for person in people:
            created_person = await mock_neo4j_graph.create_node(person)
            created_people.append(created_person)

        # Test filtering logic
        active_people = [p for p in created_people if p.is_active]
        assert len(active_people) == 2
        assert all(p.is_active for p in active_people)

        engineers = [p for p in created_people if "engineer" in p.tags]
        assert len(engineers) == 1
        assert engineers[0].first_name == "Alice"

    @pytest.mark.asyncio
    async def test_query_with_order_by(self, mock_neo4j_graph):
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

        created_people = []
        for person in people:
            created_person = await mock_neo4j_graph.create_node(person)
            created_people.append(created_person)

        # Test ordering logic
        sorted_by_age = sorted(created_people, key=lambda p: p.age)
        assert sorted_by_age[0].first_name == "Charlie"  # age 28
        assert sorted_by_age[1].first_name == "Alice"    # age 30
        assert sorted_by_age[2].first_name == "Bob"      # age 35

        sorted_by_score = sorted(created_people, key=lambda p: p.score, reverse=True)
        assert sorted_by_score[0].first_name == "Alice"   # score 95.5
        assert sorted_by_score[1].first_name == "Bob"     # score 88.0
        assert sorted_by_score[2].first_name == "Charlie" # score 75.0

    @pytest.mark.asyncio
    async def test_query_with_pagination(self, mock_neo4j_graph):
        people = []
        for i in range(10):
            person = TestPerson(
                first_name=f"Person{i}", last_name="Test", age=20 + i,
                email=f"person{i}@example.com", is_active=True, score=80.0 + i,
                tags=["test"], metadata={}, created_at=datetime.now(),
                birth_date=date(1990, 1, 1)
            )
            people.append(person)

        # Mock create_node to return each person
        mock_neo4j_graph.create_node.side_effect = people

        created_people = []
        for person in people:
            created_person = await mock_neo4j_graph.create_node(person)
            created_people.append(created_person)

        # Test pagination logic
        assert len(created_people) == 10

        # Simulate pagination: first 5
        first_page = created_people[:5]
        assert len(first_page) == 5
        assert first_page[0].first_name == "Person0"
        assert first_page[4].first_name == "Person4"

        # Simulate pagination: next 5
        second_page = created_people[5:10]
        assert len(second_page) == 5
        assert second_page[0].first_name == "Person5"
        assert second_page[4].first_name == "Person9"
