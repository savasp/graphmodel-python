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

"""Basic functionality tests for the graph model core."""

from datetime import date, datetime

import pytest

from graph_model import node, relationship
from graph_model.core.node import Node
from graph_model.core.relationship import Relationship, RelationshipDirection
from tests.conftest import _models

# Use the new test models
models = _models()
TestPerson = models['TestPerson']
TestAddress = models['TestAddress']
KnowsRelationship = models['KnowsRelationship']
WorksAtRelationship = models['WorksAtRelationship']


# Test classes are defined in conftest.py and imported above


class TestNodeCreation:
    """Test node creation and basic functionality."""

    def test_node_creation_with_defaults(self):
        """Test creating a node with default values."""
        person = TestPerson(
            first_name="Alice",
            last_name="Smith",
            age=0,
            email="alice@example.com",
            is_active=True,
            score=0.0,
            tags=[],
            metadata={},
            created_at=datetime.now(),
            birth_date=date(1990, 1, 1)
        )

        assert person.first_name == "Alice"
        assert person.last_name == "Smith"
        assert person.age == 0
        assert person.email == "alice@example.com"
        assert person.is_active is True
        assert person.score == 0.0
        assert person.tags == []
        assert person.metadata == {}
        assert len(person.id) == 32  # UUID hex string

    def test_node_creation_with_values(self):
        """Test creating a node with specific values."""
        person = TestPerson(
            first_name="Bob",
            last_name="Jones",
            age=30,
            email="bob@example.com",
            is_active=True,
            score=85.5,
            tags=["Python", "GraphQL"],
            metadata={"department": "Engineering"},
            created_at=datetime.now(),
            birth_date=date(1993, 5, 20)
        )

        assert person.first_name == "Bob"
        assert person.last_name == "Jones"
        assert person.age == 30
        assert person.email == "bob@example.com"
        assert person.is_active is True
        assert person.score == 85.5
        assert person.tags == ["Python", "GraphQL"]
        assert person.metadata == {"department": "Engineering"}

    def test_node_metadata(self):
        """Test that node metadata is correctly stored."""
        # Test that the node class has the expected structure
        assert hasattr(TestPerson, '__annotations__')
        assert 'first_name' in TestPerson.__annotations__
        assert 'last_name' in TestPerson.__annotations__
        assert 'age' in TestPerson.__annotations__


class TestRelationshipCreation:
    """Test relationship creation and basic functionality."""

    def test_relationship_creation(self):
        """Test creating a relationship."""
        person1 = TestPerson(
            first_name="Alice", last_name="Smith", age=30,
            email="alice@example.com", is_active=True, score=95.5,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=date(1993, 5, 20)
        )
        person2 = TestPerson(
            first_name="Bob", last_name="Jones", age=35,
            email="bob@example.com", is_active=True, score=88.0,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=date(1988, 3, 15)
        )

        relationship = KnowsRelationship(
            start_node_id=person1.id,
            end_node_id=person2.id,
            since=datetime.now(),
            strength=0.8
        )

        assert relationship.start_node_id == person1.id
        assert relationship.end_node_id == person2.id
        assert relationship.strength == 0.8
        assert len(relationship.id) == 32  # UUID hex string

    def test_relationship_metadata(self):
        """Test that relationship metadata is correctly stored."""
        # Test that the relationship class has the expected structure
        assert hasattr(KnowsRelationship, '__annotations__')
        assert 'since' in KnowsRelationship.__annotations__
        assert 'strength' in KnowsRelationship.__annotations__


class TestFieldTypes:
    """Test different field types work correctly."""

    def test_string_field(self):
        """Test that string fields work."""
        person = TestPerson(
            first_name="Test", last_name="User", age=25,
            email="test@example.com", is_active=True, score=80.0,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=date(1998, 1, 1)
        )
        assert person.first_name == "Test"
        assert person.last_name == "User"
        assert person.email == "test@example.com"

    def test_numeric_fields(self):
        """Test that numeric fields work."""
        person = TestPerson(
            first_name="Test", last_name="User", age=25,
            email="test@example.com", is_active=True, score=85.5,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=date(1998, 1, 1)
        )
        assert person.age == 25
        assert person.score == 85.5

    def test_boolean_field(self):
        """Test that boolean fields work."""
        person = TestPerson(
            first_name="Test", last_name="User", age=25,
            email="test@example.com", is_active=False, score=80.0,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=date(1998, 1, 1)
        )
        assert person.is_active is False

    def test_list_field(self):
        """Test that list fields work."""
        person = TestPerson(
            first_name="Test", last_name="User", age=25,
            email="test@example.com", is_active=True, score=80.0,
            tags=["Python", "GraphQL"], metadata={}, created_at=datetime.now(),
            birth_date=date(1998, 1, 1)
        )
        assert person.tags == ["Python", "GraphQL"]

    def test_dict_field(self):
        """Test that dict fields work."""
        person = TestPerson(
            first_name="Test", last_name="User", age=25,
            email="test@example.com", is_active=True, score=80.0,
            tags=[], metadata={"department": "Engineering"}, created_at=datetime.now(),
            birth_date=date(1998, 1, 1)
        )
        assert person.metadata == {"department": "Engineering"}

    def test_datetime_field(self):
        """Test that datetime fields work."""
        now = datetime.now()
        person = TestPerson(
            first_name="Test", last_name="User", age=25,
            email="test@example.com", is_active=True, score=80.0,
            tags=[], metadata={}, created_at=now,
            birth_date=date(1998, 1, 1)
        )
        assert person.created_at == now

    def test_date_field(self):
        """Test that date fields work."""
        birth_date = date(1998, 1, 1)
        person = TestPerson(
            first_name="Test", last_name="User", age=25,
            email="test@example.com", is_active=True, score=80.0,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=birth_date
        )
        assert person.birth_date == birth_date


class TestImmutability:
    """Test relationship immutability."""

    def test_relationship_immutable(self):
        """Test that relationships are immutable once created."""
        person1 = TestPerson(
            first_name="Alice", last_name="Smith", age=30,
            email="alice@example.com", is_active=True, score=95.5,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=date(1993, 5, 20)
        )
        person2 = TestPerson(
            first_name="Bob", last_name="Jones", age=35,
            email="bob@example.com", is_active=True, score=88.0,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=date(1988, 3, 15)
        )

        relationship = KnowsRelationship(
            start_node_id=person1.id,
            end_node_id=person2.id,
            since=datetime.now(),
            strength=1.0
        )

        # Should not be able to modify core relationship properties
        # Pydantic raises ValidationError for frozen models
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            relationship.start_node_id = "different_id"

        with pytest.raises(ValidationError):
            relationship.end_node_id = "different_id"


if __name__ == "__main__":
    pytest.main([__file__])
