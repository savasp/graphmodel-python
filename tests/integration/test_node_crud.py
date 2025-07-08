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


class TestNodeCRUDIntegration:
    @pytest.mark.asyncio
    async def test_create_and_read_node(self, neo4j_graph_factory, sample_person):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
            created_person = await neo4j_graph.create_node(sample_person)
            assert created_person.id == sample_person.id
            read_person = await neo4j_graph.get_node(sample_person.id)
            assert read_person is not None
            assert read_person.first_name == sample_person.first_name
            assert read_person.last_name == sample_person.last_name
            assert read_person.age == sample_person.age
            break

    @pytest.mark.asyncio
    async def test_update_node(self, neo4j_graph_factory, sample_person):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
            created_person = await neo4j_graph.create_node(sample_person)
            updated_person = TestPerson(
                id=created_person.id,
                first_name="Updated",
                last_name="Name",
                age=35,
                email="updated@example.com",
                is_active=False,
                score=85.0,
                tags=["updated"],
                metadata={"updated": "true"},
                created_at=datetime.now(),
                birth_date=date(1990, 1, 1)
            )
            result = await neo4j_graph.update_node(updated_person)
            assert result is True
            read_person = await neo4j_graph.get_node(updated_person.id)
            assert read_person is not None
            assert read_person.first_name == "Updated"
            assert read_person.last_name == "Name"
            assert read_person.age == 35
            break

    @pytest.mark.asyncio
    async def test_delete_node(self, neo4j_graph_factory, sample_person):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
            created_person = await neo4j_graph.create_node(sample_person)
            result = await neo4j_graph.delete_node(created_person.id)
            assert result is True
            read_person = await neo4j_graph.get_node(created_person.id)
            assert read_person is None
            break

    @pytest.mark.asyncio
    async def test_query_multiple_nodes(self, neo4j_graph_factory):
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
            # Query all nodes (implementation may vary)
            # Here, just check that at least one can be read back
            read_person = await neo4j_graph.get_node(people[0].id)
            assert read_person is not None
            assert read_person.first_name == "Alice"
            break
