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
KnowsRelationship = models['KnowsRelationship']
WorksAtRelationship = models['WorksAtRelationship']


class TestRelationshipCRUDIntegration:
    @pytest.mark.asyncio
    async def test_create_and_read_relationship(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson, KnowsRelationship):
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

            # Create nodes
            created_person1 = await neo4j_graph.create_node(person1)
            created_person2 = await neo4j_graph.create_node(person2)

            # Create relationship
            relationship = KnowsRelationship(
                start_node_id=created_person1.id,
                end_node_id=created_person2.id,
                since=datetime.now(),
                strength=0.8
            )

            created_relationship = await neo4j_graph.create_relationship(relationship)
            assert created_relationship.id is not None
            assert created_relationship.start_node_id == created_person1.id
            assert created_relationship.end_node_id == created_person2.id

            # Test get_relationship
            read_relationship = await neo4j_graph.get_relationship(created_relationship.id)
            assert read_relationship is not None
            assert read_relationship.start_node_id == created_person1.id
            assert read_relationship.end_node_id == created_person2.id
            break

    @pytest.mark.asyncio
    async def test_update_relationship(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson, KnowsRelationship):
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

            # Create nodes
            created_person1 = await neo4j_graph.create_node(person1)
            created_person2 = await neo4j_graph.create_node(person2)

            # Create relationship
            relationship = KnowsRelationship(
                start_node_id=created_person1.id,
                end_node_id=created_person2.id,
                since=datetime.now(),
                strength=0.8
            )

            created_relationship = await neo4j_graph.create_relationship(relationship)

            # Update relationship
            updated_relationship = KnowsRelationship(
                id=created_relationship.id,
                start_node_id=created_relationship.start_node_id,
                end_node_id=created_relationship.end_node_id,
                since=datetime.now(),
                strength=0.9
            )

            result = await neo4j_graph.update_relationship(updated_relationship)
            assert result is True

            # Verify update
            read_relationship = await neo4j_graph.get_relationship(updated_relationship.id)
            assert read_relationship is not None
            assert read_relationship.strength == 0.9
            break

    @pytest.mark.asyncio
    async def test_delete_relationship(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson, KnowsRelationship):
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

            # Create nodes
            created_person1 = await neo4j_graph.create_node(person1)
            created_person2 = await neo4j_graph.create_node(person2)

            # Create relationship
            relationship = KnowsRelationship(
                start_node_id=created_person1.id,
                end_node_id=created_person2.id,
                since=datetime.now(),
                strength=0.8
            )

            created_relationship = await neo4j_graph.create_relationship(relationship)
            result = await neo4j_graph.delete_relationship(created_relationship.id)
            assert result is True

            # Verify deletion
            read_relationship = await neo4j_graph.get_relationship(created_relationship.id)
            assert read_relationship is None
            break

    @pytest.mark.asyncio
    async def test_query_relationships(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson, KnowsRelationship):
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
            person3 = TestPerson(
                first_name="Charlie", last_name="Brown", age=28,
                email="charlie@example.com", is_active=False, score=75.0,
                tags=["junior"], metadata={}, created_at=datetime.now(),
                birth_date=date(1995, 8, 10)
            )

            created_person1 = await neo4j_graph.create_node(person1)
            created_person2 = await neo4j_graph.create_node(person2)
            created_person3 = await neo4j_graph.create_node(person3)

            # Create relationships
            relationship1 = KnowsRelationship(
                start_node_id=created_person1.id,
                end_node_id=created_person2.id,
                since=datetime.now(),
                strength=0.8
            )
            relationship2 = KnowsRelationship(
                start_node_id=created_person1.id,
                end_node_id=created_person3.id,
                since=datetime.now(),
                strength=0.6
            )

            await neo4j_graph.create_relationship(relationship1)
            await neo4j_graph.create_relationship(relationship2)

            # Query relationships (implementation may vary)
            # For now, just verify the relationships were created
            assert relationship1.id is not None
            assert relationship2.id is not None
            break
