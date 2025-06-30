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
Examples demonstrating query expressions for embedded vs related properties.

This shows how the same query syntax translates to different underlying operations
depending on whether properties are embedded or stored as related nodes.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from graph_model import (
    Node,
    Relationship,
    embedded_field,
    node,
    property_field,
    related_node_field,
    relationship,
)
from graph_model.providers.neo4j import Neo4jDriver, Neo4jGraph


@node(label="ContactInfo")
class ContactInfo(Node):
    id: str = property_field()
    email: str = property_field()
    phone: Optional[str] = property_field(default=None)
    city: str = property_field()


@node(label="Address")
class Address(Node):
    id: str = property_field()
    street: str = property_field()
    city: str = property_field()
    state: str = property_field()
    country: str = property_field()
    zip_code: str = property_field()


@node(label="Person")
class Person(Node):
    first_name: str = property_field(indexed=True)
    last_name: str = property_field(indexed=True)
    age: int = property_field()

    # EMBEDDED PROPERTY - stored as JSON on the Person node
    contact_info: ContactInfo = embedded_field()
    tags: List[str] = property_field()

    # RELATED NODE PROPERTIES - stored as separate nodes
    home_address: Optional[Address] = related_node_field(
        relationship_type="HAS_HOME_ADDRESS",
        private=True,  # Private - not discoverable in normal graph traversal
        required=False,
        default=None
    )
    work_addresses: List[Address] = related_node_field(
        relationship_type="WORKS_AT_ADDRESS",
        private=False,  # Public - discoverable in normal graph traversal
        required=True,
        default_factory=list
    )


@relationship(label="LIVES_IN")
class LivesIn(Relationship):
    since: datetime


async def demonstrate_query_differences():
    print("=== QUERY EXAMPLES: EMBEDDED vs RELATED PROPERTIES (Live) ===\n")

    # 1. Initialize Neo4j driver
    print("1. INITIALIZING NEO4J DRIVER")
    await Neo4jDriver.initialize(
        uri="neo4j://localhost:7687",
        user="neo4j",
        password="password",
        database="QueryingExamples"
    )
    await Neo4jDriver.ensure_database_exists()
    graph = Neo4jGraph()
    print("   ✓ Driver initialized\n")

    # 0. Clean up database before running
    print("0. CLEANING UP DATABASE")
    await graph._driver._driver.execute_query(
        "MATCH (n) DETACH DELETE n"
    )
    print("   ✓ Database cleaned\n")

    # 2. Create sample data
    print("2. CREATING SAMPLE DATA")
    addr_portland = Address(id="addr-portland", street="123 Main St", city="Portland", state="OR", country="USA", zip_code="97201")
    addr_seattle = Address(id="addr-seattle", street="456 Pine St", city="Seattle", state="WA", country="USA", zip_code="98101")
    addr_boston = Address(id="addr-boston", street="789 Beacon St", city="Boston", state="MA", country="USA", zip_code="02101")
    alice = Person(
        id="alice-1",
        first_name="Alice",
        last_name="Smith",
        age=30,
        contact_info=ContactInfo(id="contact-alice", email="alice@example.com", city="Portland"),
        tags=["engineer", "python"],
        home_address=addr_portland,
        work_addresses=[addr_seattle]
    )
    bob = Person(
        id="bob-2",
        first_name="Bob",
        last_name="Jones",
        age=40,
        contact_info=ContactInfo(id="contact-bob", email="bob@example.com", city="Boston"),
        tags=["manager", "java"],
        home_address=addr_boston,
        work_addresses=[addr_portland, addr_seattle]
    )
    await graph.create_node(addr_portland)
    await graph.create_node(addr_seattle)
    await graph.create_node(addr_boston)
    await graph.create_node(alice)
    await graph.create_node(bob)
    print("   ✓ Sample data created\n")

    # 3. Embedded property queries
    print("3. EMBEDDED PROPERTY QUERIES (Live)")
    print("People in Portland (embedded contact_info.city):")
    people_in_portland = await graph.nodes(Person).where(lambda p: p.contact_info.city == "Portland").to_list()
    for p in people_in_portland:
        print(f"  {p.first_name} {p.last_name} (city: {p.contact_info.city})")
    print()

    print("People with 'engineer' tag (embedded list):")
    engineers = await graph.nodes(Person).where(lambda p: "engineer" in p.tags).to_list()
    for p in engineers:
        print(f"  {p.first_name} {p.last_name} (tags: {p.tags})")
    print()

    # 4. Related node property queries
    print("4. RELATED NODE PROPERTY QUERIES (Live)")
    print("People in Portland (related home_address.city):")
    people_in_portland_home = await graph.nodes(Person).where(lambda p: p.home_address.city == "Portland").to_list()
    for p in people_in_portland_home:
        print(f"  {p.first_name} {p.last_name} (home city: {p.home_address.city})")
    print()

    print("People who work in Seattle (related work_addresses):")
    seattle_workers = await graph.nodes(Person).where(lambda p: any(addr.city == "Seattle" for addr in p.work_addresses)).to_list()
    for p in seattle_workers:
        print(f"  {p.first_name} {p.last_name} (work cities: {[addr.city for addr in p.work_addresses]})")
    print()

    # 5. Complex nested queries
    print("5. COMPLEX NESTED QUERIES (Live)")
    print("Engineers in Portland (embedded tag + related address):")
    portland_engineers = await (graph.nodes(Person)
        .where(lambda p: "engineer" in p.tags)
        .where(lambda p: p.home_address.city == "Portland")
        .to_list())
    for p in portland_engineers:
        print(f"  {p.first_name} {p.last_name} (tags: {p.tags}, home city: {p.home_address.city})")
    print()

    print("=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(demonstrate_query_differences())
