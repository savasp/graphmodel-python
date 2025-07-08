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

"""
Neo4j implementation of node queryable interface.

This module provides the Neo4j-specific implementation of the node queryable
interface, translating LINQ-style operations to Cypher queries.
"""

from typing import Any, Callable, Generic, List, Optional, Type, TypeVar

from graph_model.attributes.decorators import get_relationship_label

from ...core.entity import IEntity
from ...querying.queryable import IOrderedGraphNodeQueryable
from .cypher_builder import CypherBuilder
from .serialization import Neo4jSerializer

N = TypeVar("N", bound=IEntity)


class Neo4jNodeQueryable(IOrderedGraphNodeQueryable[N], Generic[N]):
    """
    Neo4j implementation of node queryable interface.

    Provides LINQ-style querying capabilities for nodes in Neo4j,
    translating lambda expressions to Cypher queries.
    """

    def __init__(self, node_type: Type[N], session: Any):
        """
        Initialize the node queryable.

        Args:
            node_type: Type of nodes to query.
            session: Neo4j session for executing queries.
        """
        self._node_type = node_type
        self._session = session
        self._cypher_builder = CypherBuilder(node_type)

        # Query state
        self._where_predicate: Optional[Callable] = None
        self._order_by_key: Optional[Callable] = None
        self._order_descending: bool = False
        self._take_limit: Optional[int] = None
        self._skip_count: Optional[int] = None
        self._select_projection: Optional[Callable] = None
        self._traversal_relationship: Optional[str] = None
        self._traversal_target_type: Optional[Type] = None
        self._traversal_depth: Optional[int] = None

    def where(self, predicate: Callable[[N], bool]) -> "Neo4jNodeQueryable[N]":
        """
        Filter nodes based on a predicate.

        Args:
            predicate: Lambda expression defining the filter condition.

        Returns:
            Self for method chaining.
        """
        self._where_predicate = predicate
        return self

    def order_by(self, key_selector: Callable[[N], Any]) -> "Neo4jNodeQueryable[N]":
        """
        Order nodes by a key selector in ascending order.

        Args:
            key_selector: Lambda expression defining the sort key.

        Returns:
            Self for method chaining.
        """
        self._order_by_key = key_selector
        self._order_descending = False
        return self

    def order_by_descending(self, key_selector: Callable[[N], Any]) -> "Neo4jNodeQueryable[N]":
        """
        Order nodes by a key selector in descending order.

        Args:
            key_selector: Lambda expression defining the sort key.

        Returns:
            Self for method chaining.
        """
        self._order_by_key = key_selector
        self._order_descending = True
        return self

    def take(self, count: int) -> "Neo4jNodeQueryable[N]":
        """
        Limit the number of results.

        Args:
            count: Maximum number of results to return.

        Returns:
            Self for method chaining.
        """
        self._take_limit = count
        return self

    def skip(self, count: int) -> "Neo4jNodeQueryable[N]":
        """
        Skip a number of results.

        Args:
            count: Number of results to skip.

        Returns:
            Self for method chaining.
        """
        self._skip_count = count
        return self

    def select(self, selector: Callable[[N], Any]) -> "Neo4jNodeQueryable[Any]":
        """
        Project results using a selector function.

        Args:
            selector: Lambda expression defining the projection.

        Returns:
            A new queryable with projected results.
        """
        self._select_projection = selector
        return self

    def traverse(self, relationship_type, target_type: Type) -> "Neo4jNodeQueryable[N]":
        """
        Traverse relationships to target nodes.

        Args:
            relationship_type: Type of relationship to traverse (class or string).
            target_type: Type of target nodes.

        Returns:
            Self for method chaining.
        """
        # Accept either a class or a string for relationship_type
        if isinstance(relationship_type, str):
            rel_label = relationship_type
        else:
            rel_label = get_relationship_label(relationship_type)
        self._traversal_relationship = rel_label
        self._traversal_target_type = target_type
        return self

    def with_depth(self, depth: int) -> "Neo4jNodeQueryable[N]":
        """
        Set traversal depth for relationship traversal.

        Args:
            depth: Maximum traversal depth.

        Returns:
            Self for method chaining.
        """
        self._traversal_depth = depth
        return self

    async def to_list(self) -> List[N]:
        """
        Execute the query and return results as a list.

        Returns:
            List of nodes matching the query criteria.
        """
        # Build Cypher query using CypherBuilder
        cypher_query = self._cypher_builder.build_query(
            where_predicate=self._where_predicate,
            order_by_key=self._order_by_key,
            order_descending=self._order_descending,
            take_count=self._take_limit,
            skip_count=self._skip_count,
            include_complex_properties=True,
            traversal_relationship=self._traversal_relationship,
            traversal_target_type=self._traversal_target_type,
            select_projection=self._select_projection
        )

        print(f"DEBUG node_queryable: cypher_query = {cypher_query.query}")
        print(f"DEBUG node_queryable: parameters = {cypher_query.parameters}")

        # Execute query
        result = await self._session.run(cypher_query.query, cypher_query.parameters)
        data = await result.data()

        # Convert results to node objects
        nodes = []
        for record in data:
            if self._node_type.__name__ == "Person":
                print("DEBUG Neo4j record (Person):", record)  # Debug print
            # If this is a projection (select() was used), return the projected data directly
            if self._select_projection:
                nodes.append(record)
            else:
                if "n" in record:
                    # Extract complex properties from the record
                    complex_properties = {}
                    for field_name in self._cypher_builder.complex_properties.keys():
                        if field_name in record:
                            complex_properties[field_name] = record[field_name]

                    # Deserialize the node with complex properties
                    node = Neo4jSerializer.deserialize_node(
                        record["n"],
                        self._node_type,
                        complex_properties
                    )
                else:
                    node = self._node_type(**record)
                nodes.append(node)

        # Apply projection if select() was used (already handled above)
        return nodes

    async def first(self) -> N:
        """
        Get the first result or raise an exception if none found.

        Returns:
            The first node matching the criteria.

        Raises:
            Exception: If no results are found.
        """
        results = await self.take(1).to_list()
        if not results:
            raise Exception("No results found")
        return results[0]

    async def first_or_none(self) -> Optional[N]:
        """
        Get the first result or None if none found.

        Returns:
            The first node matching the criteria, or None.
        """
        try:
            return await self.first()
        except Exception:
            return None

    def order_by_desc(self, key_func: Callable[[N], Any]) -> "Neo4jNodeQueryable[N]":
        """
        Orders elements by the specified key function in descending order.

        Args:
            key_func: A function that extracts the ordering key from an element.

        Returns:
            A new ordered queryable.
        """
        return self.order_by_descending(key_func)

    async def count(self) -> int:
        """
        Returns the number of elements in the query.

        Returns:
            The count of elements.
        """
        cypher_query = self._cypher_builder.build_count_query()
        result = await self._session.run(cypher_query.query, cypher_query.parameters)  # type: ignore
        records = await result.data()  # type: ignore
        return records[0]['count'] if records else 0

    async def any(self) -> bool:
        """
        Determines whether any elements exist.

        Returns:
            True if any elements exist, False otherwise.
        """
        return await self.count() > 0

    async def all(self, predicate: Callable[[N], bool]) -> bool:
        """
        Determines whether all elements satisfy a condition.

        Args:
            predicate: A function to test each element for a condition.

        Returns:
            True if all elements satisfy the condition, False otherwise.
        """
        # This is a simplified implementation
        # In practice, you'd want to build a more efficient Cypher query
        results = await self.to_list()
        return all(predicate(item) for item in results)

    def group_by(self, key_selector: Callable[[N], Any]) -> "Neo4jNodeQueryable[Any]":
        """
        Groups elements by a key selector function.

        Args:
            key_selector: A function that extracts the grouping key from each element.

        Returns:
            A new queryable of grouped results.
        """
        # This is a simplified implementation that would need proper Cypher generation
        new_queryable = Neo4jNodeQueryable(self._node_type, self._session)
        # In practice, you'd add GROUP BY to the Cypher builder
        return new_queryable  # type: ignore

    def aggregate(self) -> Any:
        """
        Creates an aggregation builder for this queryable.

        Returns:
            An AggregationBuilder for constructing aggregation queries.
        """
        # This would return a proper aggregation builder in a full implementation
        raise NotImplementedError("Aggregation not yet implemented")

    def as_async_queryable(self) -> Any:
        """
        Converts this queryable to an async queryable for streaming operations.

        Returns:
            An async queryable for streaming query execution.
        """
        # This would return a proper async queryable in a full implementation
        return self

    def __aiter__(self):
        """
        Returns an async iterator for streaming query results.

        Returns:
            Async iterator over query results.
        """
        # This would return a proper async iterator in a full implementation
        return self._async_iter()

    async def _async_iter(self):
        """Internal async iterator implementation."""
        results = await self.to_list()
        for result in results:
            yield result

    def then_by(self, key_func: Callable[[N], Any]) -> "Neo4jNodeQueryable[N]":
        """
        Performs a subsequent ordering of the elements in ascending order.

        Args:
            key_func: A function that extracts the ordering key from an element.

        Returns:
            A new ordered queryable with the additional ordering applied.
        """
        # This is a simplified implementation
        new_queryable = Neo4jNodeQueryable(self._node_type, self._session)
        # In practice, you'd add additional ORDER BY to the Cypher builder
        return new_queryable

    def then_by_desc(self, key_func: Callable[[N], Any]) -> "Neo4jNodeQueryable[N]":
        """
        Performs a subsequent ordering of the elements in descending order.

        Args:
            key_func: A function that extracts the ordering key from an element.

        Returns:
            A new ordered queryable with the additional ordering applied.
        """
        # This is a simplified implementation
        new_queryable = Neo4jNodeQueryable(self._node_type, self._session)
        # In practice, you'd add additional ORDER BY DESC to the Cypher builder
        return new_queryable
