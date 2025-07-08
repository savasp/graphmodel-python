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
Example demonstrating the new annotation-based API.

This example shows how to use the simplified domain data type definitions
with annotation-only style, similar to the .NET approach.
"""

import asyncio
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

from graph_model.core import Node, Relationship
from graph_model.providers.neo4j import Neo4jDriver


class Address(BaseModel):
    """Complex embedded object."""
    street: str
    city: str
    country: str
    postal_code: str


class Person(Node):
    """Person node with various field types."""
    name: str
    email: str
    age: int
    address: Address  # Complex embedded object
    phone_numbers: List[str]  # Collection of simple types
    tags: List[str] = Field(default_factory=list)
    is_active: bool = True
    metadata: Optional[dict] = None


class Knows(Relationship):
    """Knows relationship between people."""
    since: str
    strength: int = Field(ge=1, le=10)
    context: Optional[str] = None


async def main():
    """Demonstrate the new annotation-based API."""
    print("=== New Annotation-Based API Example ===\n")

    # Initialize the graph
    driver = Neo4jDriver()

    try:
        # Create a person with complex properties
        person1 = Person(
            id=str(uuid4()),
            name="Alice Johnson",
            email="alice@example.com",
            age=30,
            address=Address(
                street="123 Main St",
                city="San Francisco",
                country="USA",
                postal_code="94102"
            ),
            phone_numbers=["+1-555-0123", "+1-555-0124"],
            tags=["developer", "python"]
        )

        print(f"Created person: {person1.name}")
        print(f"  Email: {person1.email}")
        print(f"  Age: {person1.age}")
        print(f"  Address: {person1.address.street}, {person1.address.city}")
        print(f"  Phone: {person1.phone_numbers}")
        print(f"  Tags: {person1.tags}")
        print()

        # Create another person
        person2 = Person(
            id=str(uuid4()),
            name="Bob Smith",
            email="bob@example.com",
            age=28,
            address=Address(
                street="456 Oak Ave",
                city="New York",
                country="USA",
                postal_code="10001"
            ),
            phone_numbers=["+1-555-0567"],
            tags=["designer", "ui"]
        )

        print(f"Created person: {person2.name}")
        print(f"  Email: {person2.email}")
        print(f"  Age: {person2.age}")
        print(f"  Address: {person2.address.street}, {person2.address.city}")
        print(f"  Phone: {person2.phone_numbers}")
        print(f"  Tags: {person2.tags}")
        print()

        # Create a relationship between them
        knows_rel = Knows(
            id=str(uuid4()),
            start_node_id=person1.id,
            end_node_id=person2.id,
            since="2023-01-15",
            strength=5
        )

        print(f"Created relationship: {person1.name} knows {person2.name}")
        print(f"  Since: {knows_rel.since}")
        print(f"  Strength: {knows_rel.strength}")
        print()

        # Save to graph (this would normally connect to Neo4j)
        print("Note: This example demonstrates the API structure.")
        print("To actually save to Neo4j, you would use:")
        print("  await graph.create_node(person1)")
        print("  await graph.create_node(person2)")
        print("  await graph.create_relationship(knows_rel)")
        print()

        # Demonstrate field metadata access
        print("=== Field Metadata ===")
        person_fields = Person.model_fields
        for field_name, field in person_fields.items():
            if field_name == 'id':
                continue  # Skip the base id field

            print(f"Field: {field_name}")
            print(f"  Type: {field.annotation}")
            print(f"  Required: {field.is_required()}")
            print(f"  Default: {field.default}")
            print()

        print("=== Relationship Metadata ===")
        knows_fields = Knows.model_fields
        for field_name, field in knows_fields.items():
            if field_name in ['id', 'start_node_id', 'end_node_id']:
                continue  # Skip the base fields

            print(f"Field: {field_name}")
            print(f"  Type: {field.annotation}")
            print(f"  Required: {field.is_required()}")
            print(f"  Default: {field.default}")
            print()

        # Demonstrate type detection
        print("=== Type Detection ===")
        from graph_model.core import TypeDetector

        print(f"Person.name is simple: {TypeDetector.is_simple_type(Person.model_fields['name'].annotation)}")
        print(f"Person.address is complex: {TypeDetector.is_complex_type(Person.model_fields['address'].annotation)}")
        print(f"Person.phone_numbers is collection: {TypeDetector.is_collection_of_simple(Person.model_fields['phone_numbers'].annotation)}")
        print()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up
        await driver.close()


if __name__ == "__main__":
    asyncio.run(main())
