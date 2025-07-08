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


class TestQueryingIntegration:
    """Test querying functionality with real Neo4j database."""

    @pytest.mark.asyncio
    async def test_query_all_nodes(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
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

            for person in people:
                await neo4j_graph.create_node(person)

            for person in people:
                read_person = await neo4j_graph.get_node(person.id)
                assert read_person is not None
                assert read_person.first_name in ["Alice", "Bob", "Charlie"]
            break

    @pytest.mark.asyncio
    async def test_query_with_filtering(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
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

            for person in people:
                await neo4j_graph.create_node(person)

            all_people = []
            for person in people:
                read_person = await neo4j_graph.get_node(person.id)
                if read_person is not None:
                    all_people.append(read_person)

            active_people = [p for p in all_people if p.is_active]
            assert len(active_people) == 2
            assert all(p.is_active for p in active_people)

            engineers = [p for p in all_people if "engineer" in p.tags]
            assert len(engineers) == 1
            assert engineers[0].first_name == "Alice"
            break

    @pytest.mark.asyncio
    async def test_query_with_ordering(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
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

            for person in people:
                await neo4j_graph.create_node(person)

            all_people = []
            for person in people:
                read_person = await neo4j_graph.get_node(person.id)
                if read_person is not None:
                    all_people.append(read_person)

            sorted_by_age = sorted(all_people, key=lambda p: p.age)
            assert sorted_by_age[0].first_name == "Charlie"
            assert sorted_by_age[1].first_name == "Alice"
            assert sorted_by_age[2].first_name == "Bob"

            sorted_by_score = sorted(all_people, key=lambda p: p.score, reverse=True)
            assert sorted_by_score[0].first_name == "Alice"
            assert sorted_by_score[1].first_name == "Bob"
            assert sorted_by_score[2].first_name == "Charlie"
            break

    @pytest.mark.asyncio
    async def test_query_with_pagination(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
            people = []
            for i in range(10):
                person = TestPerson(
                    first_name=f"Person{i}", last_name="Test", age=20 + i,
                    email=f"person{i}@example.com", is_active=True, score=80.0 + i,
                    tags=["test"], metadata={}, created_at=datetime.now(),
                    birth_date=date(1990, 1, 1)
                )
                people.append(person)
                await neo4j_graph.create_node(person)

            all_people = []
            for person in people:
                read_person = await neo4j_graph.get_node(person.id)
                if read_person is not None:
                    all_people.append(read_person)

            first_page = all_people[:5]
            assert len(first_page) == 5
            assert first_page[0].first_name == "Person0"
            assert first_page[4].first_name == "Person4"

            second_page = all_people[5:10]
            assert len(second_page) == 5
            assert second_page[0].first_name == "Person5"
            assert second_page[4].first_name == "Person9"
            break
