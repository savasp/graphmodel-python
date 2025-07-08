from datetime import date, datetime

import pytest

from graph_model.core.exceptions import GraphError
from tests.conftest import TestPerson


class TestErrorHandlingIntegration:
    @pytest.mark.asyncio
    async def test_create_duplicate_node(self, neo4j_graph_factory, sample_person):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
            created_person = await neo4j_graph.create_node(sample_person)
            duplicate_person = TestPerson(
                id=created_person.id,  # Use the same ID
                first_name="Duplicate", last_name="Person", age=25,
                email="duplicate@example.com", is_active=True, score=50.0,
                tags=[], metadata={}, created_at=datetime.now(),
                birth_date=date(1998, 1, 1)
            )
            try:
                await neo4j_graph.create_node(duplicate_person)
                read_person = await neo4j_graph.get_node(created_person.id)
                assert read_person is not None
                assert read_person.first_name == sample_person.first_name
            except GraphError:
                pass
            break

    @pytest.mark.asyncio
    async def test_update_nonexistent_node(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
            person = TestPerson(
                id="nonexistent-id",
                first_name="Nonexistent", last_name="Person", age=25,
                email="nonexistent@example.com", is_active=True, score=50.0,
                tags=[], metadata={}, created_at=datetime.now(),
                birth_date=date(1998, 1, 1)
            )
            try:
                await neo4j_graph.update_node(person)
                read_person = await neo4j_graph.get_node(person.id)
                assert read_person is None
            except GraphError:
                pass
            break

    @pytest.mark.asyncio
    async def test_delete_nonexistent_node(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
            person = TestPerson(
                id="nonexistent-id",
                first_name="Nonexistent", last_name="Person", age=25,
                email="nonexistent@example.com", is_active=True, score=50.0,
                tags=[], metadata={}, created_at=datetime.now(),
                birth_date=date(1998, 1, 1)
            )
            try:
                await neo4j_graph.delete_node(person.id)
                read_person = await neo4j_graph.get_node(person.id)
                assert read_person is None
            except GraphError:
                pass
            break

    @pytest.mark.asyncio
    async def test_get_nonexistent_node(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
            result = await neo4j_graph.get_node("nonexistent-id")
            assert result is None
            break

    @pytest.mark.asyncio
    async def test_invalid_data_types(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(TestPerson):
            person = TestPerson(
                first_name="Test", last_name="User", age=25,
                email="test@example.com", is_active=True, score=85.5,
                tags=["test"], metadata={"key": "value"},
                created_at=datetime.now(),
                birth_date=date(1998, 5, 20)
            )
            created_person = await neo4j_graph.create_node(person)
            assert created_person.id is not None
            try:
                invalid_person = TestPerson(
                    id=created_person.id,
                    first_name="Test", last_name="User", age="invalid_age",
                    email="test@example.com", is_active=True, score=85.5,
                    tags=["test"], metadata={"key": "value"},
                    created_at=datetime.now(),
                    birth_date=date(1998, 5, 20)
                )
                await neo4j_graph.update_node(invalid_person)
            except Exception:
                pass
            break
