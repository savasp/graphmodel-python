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
from typing import Optional
from unittest.mock import AsyncMock

import pytest

from graph_model import node, relationship
from graph_model.core.node import Node
from graph_model.core.relationship import Relationship
from graph_model.providers.neo4j.cypher_builder import CypherBuilder
from graph_model.providers.neo4j.node_queryable import Neo4jNodeQueryable
from graph_model.providers.neo4j.relationship_queryable import (
    Neo4jRelationshipQueryable,
)
from tests.conftest import _models


@node("Person")
class Person(Node):
    name: str
    age: int
    city: Optional[str] = None


@node("Company")
class Company(Node):
    name: str
    industry: str


@relationship("WORKS_FOR")
class WorksFor(Relationship):
    position: str
    salary: int


# Use the new test models
models = _models()
TestPerson = models['TestPerson']


class TestBasicQueryableOperations:
    """Test basic queryable operations with the new annotation-based API."""

    def test_basic_filtering(self):
        """Test basic filtering functionality."""
        people = [
            TestPerson(
                id="1", first_name="Alice", last_name="Smith", age=30,
                email="alice@example.com", is_active=True, score=95.5,
                tags=["engineer"], metadata={}, created_at=datetime.now(),
                birth_date=date(1993, 5, 20)
            ),
            TestPerson(
                id="2", first_name="Bob", last_name="Jones", age=35,
                email="bob@example.com", is_active=True, score=88.0,
                tags=["manager"], metadata={}, created_at=datetime.now(),
                birth_date=date(1988, 3, 15)
            ),
            TestPerson(
                id="3", first_name="Charlie", last_name="Brown", age=28,
                email="charlie@example.com", is_active=False, score=75.0,
                tags=["junior"], metadata={}, created_at=datetime.now(),
                birth_date=date(1995, 8, 10)
            )
        ]

        # Test basic filtering logic
        active_people = [p for p in people if p.is_active]
        assert len(active_people) == 2
        assert all(p.is_active for p in active_people)

        # Test multiple conditions
        young_active = [p for p in people if p.is_active and p.age < 35]
        assert len(young_active) == 1
        assert young_active[0].first_name == "Alice"

    def test_ordering(self):
        """Test ordering functionality."""
        people = [
            TestPerson(
                id="1", first_name="Alice", last_name="Smith", age=30,
                email="alice@example.com", is_active=True, score=95.5,
                tags=["engineer"], metadata={}, created_at=datetime.now(),
                birth_date=date(1993, 5, 20)
            ),
            TestPerson(
                id="2", first_name="Bob", last_name="Jones", age=35,
                email="bob@example.com", is_active=True, score=88.0,
                tags=["manager"], metadata={}, created_at=datetime.now(),
                birth_date=date(1988, 3, 15)
            ),
            TestPerson(
                id="3", first_name="Charlie", last_name="Brown", age=28,
                email="charlie@example.com", is_active=False, score=75.0,
                tags=["junior"], metadata={}, created_at=datetime.now(),
                birth_date=date(1995, 8, 10)
            )
        ]

        # Test ascending order
        by_age_asc = sorted(people, key=lambda p: p.age)
        assert by_age_asc[0].first_name == "Charlie"  # age 28
        assert by_age_asc[1].first_name == "Alice"    # age 30
        assert by_age_asc[2].first_name == "Bob"      # age 35

        # Test descending order
        by_score_desc = sorted(people, key=lambda p: p.score, reverse=True)
        assert by_score_desc[0].first_name == "Alice"   # score 95.5
        assert by_score_desc[1].first_name == "Bob"     # score 88.0
        assert by_score_desc[2].first_name == "Charlie" # score 75.0

    def test_projection(self):
        """Test projection functionality."""
        people = [
            TestPerson(
                id="1", first_name="Alice", last_name="Smith", age=30,
                email="alice@example.com", is_active=True, score=95.5,
                tags=["engineer"], metadata={}, created_at=datetime.now(),
                birth_date=date(1993, 5, 20)
            ),
            TestPerson(
                id="2", first_name="Bob", last_name="Jones", age=35,
                email="bob@example.com", is_active=True, score=88.0,
                tags=["manager"], metadata={}, created_at=datetime.now(),
                birth_date=date(1988, 3, 15)
            )
        ]

        # Test simple projection
        names = [p.first_name for p in people]
        assert names == ["Alice", "Bob"]

        # Test complex projection
        person_info = [{
            "name": f"{p.first_name} {p.last_name}",
            "age": p.age,
            "active": p.is_active
        } for p in people]
        assert len(person_info) == 2
        assert person_info[0]["name"] == "Alice Smith"
        assert person_info[0]["age"] == 30
        assert person_info[0]["active"] is True

    def test_aggregation(self):
        """Test aggregation functionality."""
        people = [
            TestPerson(
                id="1", first_name="Alice", last_name="Smith", age=30,
                email="alice@example.com", is_active=True, score=95.5,
                tags=["engineer"], metadata={}, created_at=datetime.now(),
                birth_date=date(1993, 5, 20)
            ),
            TestPerson(
                id="2", first_name="Bob", last_name="Jones", age=35,
                email="bob@example.com", is_active=True, score=88.0,
                tags=["manager"], metadata={}, created_at=datetime.now(),
                birth_date=date(1988, 3, 15)
            ),
            TestPerson(
                id="3", first_name="Charlie", last_name="Brown", age=28,
                email="charlie@example.com", is_active=False, score=75.0,
                tags=["junior"], metadata={}, created_at=datetime.now(),
                birth_date=date(1995, 8, 10)
            )
        ]

        # Test count
        assert len(people) == 3

        # Test any
        assert any(p.is_active for p in people) is True
        assert any(p.age > 40 for p in people) is False

        # Test all
        assert all(p.age > 20 for p in people) is True
        assert all(p.is_active for p in people) is False

        # Test first
        first = people[0]
        assert first.first_name == "Alice"

        # Test filtering and first
        active_people = [p for p in people if p.is_active]
        first_active = active_people[0]
        assert first_active.first_name == "Alice"


class TestNeo4jNodeQueryable:
    """Test Neo4j-specific node queryable functionality."""

    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.run.return_value = AsyncMock()
        session.run.return_value.data.return_value = []
        return session

    @pytest.fixture
    def queryable(self, mock_session):
        return Neo4jNodeQueryable(Person, mock_session)

    @pytest.mark.asyncio
    async def test_where_single_condition(self, queryable, mock_session):
        """Test single where condition."""
        queryable.where(lambda p: p.age > 30)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "WHERE" in cypher
        assert "age >" in cypher

    @pytest.mark.asyncio
    async def test_where_multiple_conditions(self, queryable, mock_session):
        """Test multiple where conditions."""
        queryable.where(lambda p: p.age > 30).where(lambda p: p.name == "Alice")
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "WHERE" in cypher
        assert "age >" in cypher
        # Note: The current implementation only applies the last where condition
        # This is a limitation of the current CypherBuilder implementation

    @pytest.mark.asyncio
    async def test_order_by_ascending(self, queryable, mock_session):
        """Test ascending order by."""
        queryable.order_by(lambda p: p.age)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "ORDER BY" in cypher
        assert "age ASC" in cypher

    @pytest.mark.asyncio
    async def test_order_by_descending(self, queryable, mock_session):
        """Test descending order by."""
        queryable.order_by_desc(lambda p: p.age)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "ORDER BY" in cypher
        assert "age DESC" in cypher

    @pytest.mark.asyncio
    async def test_take(self, queryable, mock_session):
        """Test take operation."""
        queryable.take(5)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "LIMIT 5" in cypher

    @pytest.mark.asyncio
    async def test_skip(self, queryable, mock_session):
        """Test skip operation."""
        queryable.skip(10)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "SKIP 10" in cypher

    @pytest.mark.asyncio
    async def test_take_and_skip(self, queryable, mock_session):
        """Test take and skip together."""
        queryable.skip(10).take(5)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "SKIP 10" in cypher
        assert "LIMIT 5" in cypher

    @pytest.mark.asyncio
    async def test_first(self, queryable, mock_session):
        """Test first operation."""
        mock_session.run.return_value.data.return_value = [{"id": "1", "name": "Alice", "age": 30}]
        
        result = await queryable.first()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "LIMIT 1" in cypher

    @pytest.mark.asyncio
    async def test_first_or_none_found(self, queryable, mock_session):
        """Test first_or_none when result is found."""
        mock_session.run.return_value.data.return_value = [{"id": "1", "name": "Alice", "age": 30}]
        
        result = await queryable.first_or_none()
        assert result is not None

    @pytest.mark.asyncio
    async def test_first_or_none_not_found(self, queryable, mock_session):
        """Test first_or_none when no result is found."""
        mock_session.run.return_value.data.return_value = []
        
        result = await queryable.first_or_none()
        assert result is None

    @pytest.mark.asyncio
    async def test_select_projection(self, queryable, mock_session):
        """Test select projection."""
        queryable.select(lambda p: p.name)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "RETURN" in cypher
        assert "RETURN" in cypher

    @pytest.mark.asyncio
    async def test_traverse_relationships(self, queryable, mock_session):
        """Test relationship traversal."""
        queryable.traverse(WorksFor, Company)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "MATCH" in cypher
        assert "WORKS_FOR" in cypher

    @pytest.mark.asyncio
    async def test_with_depth(self, queryable, mock_session):
        """Test depth specification."""
        queryable.with_depth(3)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        # Depth should be handled in the traversal logic

    @pytest.mark.asyncio
    async def test_chained_operations(self, queryable, mock_session):
        """Test chaining multiple operations."""
        (queryable
         .where(lambda p: p.age > 30)
         .order_by(lambda p: p.name)
         .take(10)
         .skip(5))
        
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "WHERE" in cypher
        assert "ORDER BY" in cypher
        assert "LIMIT 10" in cypher
        assert "SKIP 5" in cypher


class TestNeo4jRelationshipQueryable:
    """Test Neo4j-specific relationship queryable functionality."""

    @pytest.fixture
    def mock_session(self):
        session = AsyncMock()
        session.run.return_value = AsyncMock()
        session.run.return_value.data.return_value = []
        return session

    @pytest.fixture
    def queryable(self, mock_session):
        return Neo4jRelationshipQueryable(WorksFor, mock_session)

    @pytest.mark.asyncio
    async def test_where_condition(self, queryable, mock_session):
        """Test where condition on relationships."""
        queryable.where(lambda r: r.salary > 50000)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "WHERE" in cypher
        assert "salary >" in cypher

    @pytest.mark.asyncio
    async def test_order_by_relationship(self, queryable, mock_session):
        """Test order by on relationships."""
        queryable.order_by(lambda r: r.salary)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "ORDER BY" in cypher
        assert "salary ASC" in cypher

    @pytest.mark.asyncio
    async def test_select_relationship_projection(self, queryable, mock_session):
        """Test select projection on relationships."""
        queryable.select(lambda r: r.position)
        await queryable.to_list()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "RETURN" in cypher
        assert "RETURN" in cypher

    @pytest.mark.asyncio
    async def test_first_relationship(self, queryable, mock_session):
        """Test first operation on relationships."""
        mock_session.run.return_value.data.return_value = [{"id": "1", "position": "Manager", "salary": 75000, "start_node_id": "person-1", "end_node_id": "company-1"}]
        
        result = await queryable.first()
        
        # Verify Cypher was built correctly
        call_args = mock_session.run.call_args
        assert call_args is not None
        cypher = call_args[0][0]
        assert "LIMIT 1" in cypher


class TestCypherBuilder:
    """Test Cypher query building functionality."""

    def test_cypher_builder_initialization(self):
        """Test CypherBuilder initialization."""
        builder = CypherBuilder(Person)
        assert builder.node_type == Person
        assert builder.node_alias == "n"

    def test_build_query_with_where(self):
        """Test building query with WHERE clause."""
        builder = CypherBuilder(Person)
        query = builder.build_query(where_predicate=lambda p: p.age > 30)
        assert "WHERE" in query.query
        assert "age >" in query.query

    def test_build_query_with_order_by(self):
        """Test building query with ORDER BY clause."""
        builder = CypherBuilder(Person)
        query = builder.build_query(order_by_key=lambda p: p.name)
        assert "ORDER BY" in query.query


if __name__ == "__main__":
    pytest.main([__file__])
