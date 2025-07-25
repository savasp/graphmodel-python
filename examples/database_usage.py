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
Database usage example for the Python Graph Model library.

This example demonstrates how to specify different databases when connecting to Neo4j.
"""

import asyncio
from datetime import datetime

from graph_model import Node, Relationship, node, relationship
from graph_model.providers.neo4j import Neo4jDriver, Neo4jGraph


@node("User")
class User(Node):
    """A user in our graph model."""
    name: str
    email: str
    created_at: datetime


@relationship("FOLLOWS")
class Follows(Relationship):
    """One user follows another."""
    since: datetime


async def demonstrate_database_usage():
    """
    Demonstrate how to use different databases with Neo4j.
    """
    print("=== Database Usage Example ===")

    # Example 1: Using the default database (neo4j)
    print("\n1. Connecting to default database (neo4j):")
    try:
        await Neo4jDriver.initialize(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
            # No database specified - uses default
        )
        print("✓ Connected to default database")
    except Exception as e:
        print(f"✗ Failed to connect to default database: {e}")

    # Example 2: Using a specific database
    print("\n2. Connecting to specific database (myapp):")
    try:
        await Neo4jDriver.initialize(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password",
            database="myapp"  # Specify the database name
        )
        print("✓ Connected to 'myapp' database")
    except Exception as e:
        print(f"✗ Failed to connect to 'myapp' database: {e}")

    # Example 3: Using different databases for different operations
    print("\n3. Using different databases for different operations:")

    # Create a user for testing
    user1 = User(
        name="Alice",
        email="alice@example.com",
        created_at=datetime.now()
    )

    User(
        name="Bob",
        email="bob@example.com",
        created_at=datetime.now()
    )

    # Try to create users in different databases
    databases_to_try = ["testdatabase1", "testdatabase2", "testdatabase3"]

    for db_name in databases_to_try:
        print(f"\n   Trying database: {db_name}")
        try:
            await Neo4jDriver.initialize(
                uri="bolt://localhost:7687",
                user="neo4j",
                password="password",
                database=db_name
            )

            await Neo4jDriver.ensure_database_exists()

            graph = Neo4jGraph()

            # Try to create a user
            async with graph.transaction() as tx:
                await graph.create_node(user1, transaction=tx)
                print(f"   ✓ Successfully created user in '{db_name}' database")

        except Exception as e:
            print(f"   ✗ Failed to use '{db_name}' database: {e}")

    print("\n=== Database Usage Notes ===")
    print("• If no database is specified, Neo4j uses the default 'neo4j' database")
    print("• You can specify any database name that exists in your Neo4j instance")
    print("• Database names are case-sensitive")
    print("• You can switch databases by re-initializing the driver")
    print("• All sessions created after initialization will use the specified database")


if __name__ == "__main__":
    asyncio.run(demonstrate_database_usage())
