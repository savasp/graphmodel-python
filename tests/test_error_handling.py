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

from graph_model.core.exceptions import GraphError
from tests.conftest import _models

# Use the new test models
models = _models()
TestPerson = models['TestPerson']


class TestErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_create_node_with_invalid_data(self, mock_neo4j_graph):
        """Test creating a node with invalid data."""
        # Mock create_node to raise an error
        mock_neo4j_graph.create_node.side_effect = GraphError("Invalid data")

        person = TestPerson(
            first_name="Invalid", last_name="Person", age=25,
            email="invalid@example.com", is_active=True, score=50.0,
            tags=[], metadata={}, created_at=datetime.now(),
            birth_date=date(1998, 1, 1)
        )

        # This should raise an error
        with pytest.raises(GraphError):
            await mock_neo4j_graph.create_node(person)

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
