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
Queryable API Demo

This example demonstrates the LINQ-style queryable API structure and usage patterns
without requiring a database connection. It shows the fluent interface and method chaining.
"""

import asyncio
from typing import Optional

from graph_model import Node, Relationship, node, relationship
from graph_model.providers.neo4j import Neo4jDriver, Neo4jGraph


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


async def demonstrate_queryable_api_structure():
    print("=== Queryable API Structure Demo (Live) ===\n")

    # 1. Initialize Neo4j driver
    print("1. INITIALIZING NEO4J DRIVER")
    await Neo4jDriver.initialize(
        uri="neo4j://localhost:7687",
        user="neo4j",
        password="password",
        database="QueryableApiDemo"
    )
    await Neo4jDriver.ensure_database_exists()
    graph = Neo4jGraph()
    print("   ✓ Driver initialized\n")

    # 2. Create sample data
    print("2. CREATING SAMPLE DATA")
    alice = Person(id="alice-1", name="Alice", age=32, city="Boston")
    bob = Person(id="bob-2", name="Bob", age=45, city="San Francisco")
    carol = Person(id="carol-3", name="Carol", age=29, city="Boston")
    dave = Person(id="dave-4", name="Dave", age=38, city="Austin")
    acme = Company(id="acme-1", name="ACME Corp", industry="Technology")
    foodco = Company(id="foodco-2", name="FoodCo", industry="Food")
    worksfor1 = WorksFor(id="w1", start_node_id=alice.id, end_node_id=acme.id, position="Engineer", salary=120000)
    worksfor2 = WorksFor(id="w2", start_node_id=bob.id, end_node_id=acme.id, position="Manager", salary=150000)
    worksfor3 = WorksFor(id="w3", start_node_id=carol.id, end_node_id=foodco.id, position="Chef", salary=80000)
    worksfor4 = WorksFor(id="w4", start_node_id=dave.id, end_node_id=acme.id, position="Engineer", salary=110000)
    await graph.create_node(alice)
    await graph.create_node(bob)
    await graph.create_node(carol)
    await graph.create_node(dave)
    await graph.create_node(acme)
    await graph.create_node(foodco)
    await graph.create_relationship(worksfor1)
    await graph.create_relationship(worksfor2)
    await graph.create_relationship(worksfor3)
    await graph.create_relationship(worksfor4)
    print("   ✓ Sample data created\n")

    # 3. Node Queryable Methods
    print("3. Node Queryable Methods (Live Queries):")
    print("-" * 40)
    print("People over 30:")
    people_over_30 = await graph.nodes(Person).where(lambda p: p.age > 30).to_list()
    for p in people_over_30:
        print(f"  {p.name} (age {p.age})")
    print()

    print("People in Boston:")
    boston_people = await graph.nodes(Person).where(lambda p: p.city == "Boston").to_list()
    for p in boston_people:
        print(f"  {p.name}")
    print()

    print("People ordered by name descending:")
    people_by_name_desc = await graph.nodes(Person).order_by_descending(lambda p: p.name).to_list()
    for p in people_by_name_desc:
        print(f"  {p.name}")
    print()

    print("First 2 people:")
    first_two = await graph.nodes(Person).take(2).to_list()
    for p in first_two:
        print(f"  {p.name}")
    print()

    print("Name-age projection:")
    name_age = await graph.nodes(Person).select(lambda p: {"name": p.name, "age": p.age}).to_list()
    for entry in name_age:
        print(f"  {entry}")
    print()

    # 4. Relationship Queryable Methods
    print("4. Relationship Queryable Methods (Live Queries):")
    print("-" * 40)
    print("High-paying jobs (salary > 100k):")
    high_paying = await graph.relationships(WorksFor).where(lambda r: r.salary > 100000).to_list()
    for r in high_paying:
        print(f"  {r.position} (${r.salary})")
    print()

    print("Jobs ordered by salary descending:")
    jobs_by_salary = await graph.relationships(WorksFor).order_by_descending(lambda r: r.salary).to_list()
    for r in jobs_by_salary:
        print(f"  {r.position} (${r.salary})")
    print()

    print("Relationship projection:")
    job_summary = await graph.relationships(WorksFor).select(
        lambda r: {"position": r.position, "salary_range": "high" if r.salary > 100000 else "medium"}
    ).to_list()
    for entry in job_summary:
        print(f"  {entry}")
    print()

    print("=== Demo Complete ===")


def show_api_comparison():
    """Show comparison with traditional approaches"""

    print("\n=== API Comparison ===")
    print()

    print("Traditional Cypher:")
    print("  MATCH (p:Person)")
    print("  WHERE p.age > 30 AND p.city = 'Boston'")
    print("  ORDER BY p.name")
    print("  RETURN p")
    print("  LIMIT 10")
    print()

    print("GraphModel LINQ-style:")
    print("  await graph.nodes(Person)")
    print("      .where(lambda p: p.age > 30 and p.city == 'Boston')")
    print("      .order_by(lambda p: p.name)")
    print("      .take(10)")
    print("      .to_list()")
    print()

    print("Benefits:")
    print("  ✓ Type-safe lambda expressions")
    print("  ✓ IntelliSense support")
    print("  ✓ Compile-time error checking")
    print("  ✓ Fluent, readable syntax")
    print("  ✓ Reusable query patterns")
    print("  ✓ .NET compatibility")


if __name__ == "__main__":
    asyncio.run(demonstrate_queryable_api_structure())
    show_api_comparison()
