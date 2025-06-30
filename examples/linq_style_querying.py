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
LINQ-Style Querying Example

This example demonstrates the full LINQ-style queryable API for the GraphModel library,
showing how to perform complex queries with a familiar LINQ-like syntax.
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
    email: Optional[str] = None


@node("Company")
class Company(Node):
    name: str
    industry: str
    founded_year: int
    revenue: Optional[float] = None


@node("Skill")
class Skill(Node):
    name: str
    category: str
    difficulty_level: int


@relationship("WORKS_FOR")
class WorksFor(Relationship):
    position: str
    salary: int
    start_date: Optional[str] = None


@relationship("HAS_SKILL")
class HasSkill(Relationship):
    proficiency_level: int
    years_experience: Optional[int] = None


@relationship("KNOWS")
class Knows(Relationship):
    relationship_type: str = "colleague"


async def demonstrate_linq_style_querying():
    """Demonstrate the full LINQ-style querying capabilities"""

    print("=== LINQ-Style Querying Examples ===\n")

    # Initialize Neo4j driver
    print("1. INITIALIZING NEO4J DRIVER")
    await Neo4jDriver.initialize(
        uri="neo4j://localhost:7687",
        user="neo4j",
        password="password",
        database="LINQExamples"
    )
    await Neo4jDriver.ensure_database_exists()
    graph = Neo4jGraph()
    print("   ✓ Driver initialized\n")

    # Clean up database before running
    print("0. CLEANING UP DATABASE")
    await graph._driver._driver.execute_query(
        "MATCH (n) DETACH DELETE n"
    )
    print("   ✓ Database cleaned\n")

    # Create sample data
    print("2. CREATING SAMPLE DATA")
    await create_sample_data(graph)
    print("   ✓ Sample data created\n")

    # Demonstrate LINQ-style queries
    print("3. LINQ-STYLE QUERYING DEMONSTRATIONS")

    # Basic WHERE clauses
    print("\n   Basic WHERE clauses:")
    print("   -" * 40)

    # Find people over 30
    people_over_30 = await graph.nodes(Person).where(lambda p: p.age > 30).to_list()
    print(f"   People over 30: {len(people_over_30)} found")
    for person in people_over_30:
        print(f"     {person.name} (age {person.age})")

    # Find people in specific cities
    boston_people = await graph.nodes(Person).where(lambda p: p.city == 'Boston').to_list()
    print(f"\n   People in Boston: {len(boston_people)} found")
    for person in boston_people:
        print(f"     {person.name}")

    # Complex WHERE with multiple conditions
    senior_devs = await graph.nodes(Person).where(
        lambda p: p.age > 25 and p.city == 'San Francisco'
    ).to_list()
    print(f"\n   Senior developers in SF: {len(senior_devs)} found")
    for person in senior_devs:
        print(f"     {person.name} (age {person.age})")

    # ORDER BY operations
    print("\n   ORDER BY operations:")
    print("   -" * 40)

    # Order by age ascending
    people_by_age = await graph.nodes(Person).order_by(lambda p: p.age).to_list()
    print("   People ordered by age (ascending):")
    for person in people_by_age:
        print(f"     {person.name} (age {person.age})")

    # Order by name descending
    people_by_name_desc = await graph.nodes(Person).order_by_descending(lambda p: p.name).to_list()
    print("\n   People ordered by name (descending):")
    for person in people_by_name_desc[:3]:  # Show first 3
        print(f"     {person.name}")

    # Pagination with TAKE and SKIP
    print("\n   Pagination with TAKE and SKIP:")
    print("   -" * 40)

    # Get first 3 people
    first_three = await graph.nodes(Person).take(3).to_list()
    print("   First 3 people:")
    for person in first_three:
        print(f"     {person.name}")

    # Skip first 2, take next 2
    page_2 = await graph.nodes(Person).skip(2).take(2).to_list()
    print("\n   People 3-4 (skip 2, take 2):")
    for person in page_2:
        print(f"     {person.name}")

    # SELECT projections
    print("\n   SELECT projections:")
    print("   -" * 40)

    # Project to simple dictionary
    name_age_pairs = await graph.nodes(Person).select(
        lambda p: {'name': p.name, 'age': p.age}
    ).to_list()
    print("   Name-age pairs:")
    for pair in name_age_pairs[:3]:  # Show first 3
        print(f"     {pair}")

    # Project with computed values
    salary_info = await graph.nodes(Person).select(
        lambda p: {
            'name': p.name,
            'age_group': 'senior' if p.age > 30 else 'junior',
            'location': p.city or 'Unknown'
        }
    ).to_list()
    print("\n   Salary info with computed values:")
    for info in salary_info[:3]:  # Show first 3
        print(f"     {info}")

    # FIRST and FIRST_OR_NONE
    print("\n   FIRST and FIRST_OR_NONE:")
    print("   -" * 40)

    # Get first person
    first_person = await graph.nodes(Person).first()
    print(f"   First person: {first_person.name}")

    # Try to find someone who doesn't exist
    non_existent = await graph.nodes(Person).where(lambda p: p.name == 'NonExistent').first_or_none()
    print(f"   Non-existent person: {non_existent}")

    # Relationship queries
    print("\n   Relationship queries:")
    print("   -" * 40)

    # Find high-paying jobs
    high_paying_jobs = await graph.relationships(WorksFor).where(
        lambda r: r.salary > 100000
    ).to_list()
    print(f"   High-paying jobs (>$100k): {len(high_paying_jobs)} found")
    for job in high_paying_jobs:
        print(f"     {job.position} (${job.salary:,})")

    # Jobs ordered by salary (descending)
    print("\n   Jobs ordered by salary (descending):")
    job_summary = await (
        graph.relationships(WorksFor)
        .order_by_descending(lambda r: r.salary)
        .to_list()
    )
    for job in job_summary:
        print(job)

    # TRAVERSE relationships
    print("\n   TRAVERSE relationships:")
    print("   -" * 40)

    # Find people who work for tech companies
    tech_workers = await graph.nodes(Person).traverse('WORKS_FOR', Company).where(
        lambda target: target.industry == 'Technology'
    ).to_list()
    print(f"   People working in tech companies: {len(tech_workers)} found")
    for person in tech_workers:
        print(f"     {person.name}")

    # Find people with specific skills
    python_developers = await graph.nodes(Person).traverse('HAS_SKILL', Skill).where(
        lambda target: target.name == 'Python'
    ).to_list()
    print(f"\n   People with Python skills: {len(python_developers)} found")
    for person in python_developers:
        print(f"     {person.name}")

    # Complex chained queries
    print("\n   Complex chained queries:")
    print("   -" * 40)

    # Find senior developers in tech companies
    senior_tech_devs = await (graph.nodes(Person)
        .where(lambda p: p.age > 30)
        .traverse('WORKS_FOR', Company)
        .where(lambda target: target.industry == 'Technology')
        .order_by_descending(lambda p: p.age)
        .take(5)
        .to_list())
    print(f"   Top 5 senior tech workers: {len(senior_tech_devs)} found")
    for person in senior_tech_devs:
        print(f"     {person.name} (age {person.age})")

    # Complex relationship query with projection
    job_summary = await (graph.relationships(WorksFor)
        .where(lambda r: r.salary > 50000)
        .order_by_descending(lambda r: r.salary)
        .take(3)
        .select(lambda r: {
            'position': r.position,
            'salary_range': 'high' if r.salary > 100000 else 'medium',
            'start_date': r.start_date or 'Unknown'
        })
        .to_list())
    print("\n   Top 3 job summaries:")
    for summary in job_summary:
        print(f"     {summary}")

    print("\n=== LINQ-Style Features Summary ===")
    print("✓ Type-safe lambda expressions")
    print("✓ Fluent method chaining")
    print("✓ WHERE filtering with complex conditions")
    print("✓ ORDER BY ascending/descending")
    print("✓ TAKE/SKIP pagination")
    print("✓ SELECT projections with computed values")
    print("✓ FIRST/FIRST_OR_NONE safe access")
    print("✓ Relationship traversal")
    print("✓ Depth-limited traversal")
    print("✓ Complex chained operations")
    print("✓ Error handling patterns")

    print("\n=== .NET Compatibility ===")
    print("This API matches the .NET GraphModel LINQ implementation:")
    print("- Same method names and signatures")
    print("- Compatible lambda expression patterns")
    print("- Identical traversal and filtering concepts")
    print("- Cross-platform data compatibility")


async def create_sample_data(graph: Neo4jGraph):
    """Create sample data for the examples"""

    # Create people
    alice = Person(
        id="alice-1",
        name="Alice Johnson",
        age=28,
        city="San Francisco",
        email="alice@email.com"
    )
    bob = Person(
        id="bob-2",
        name="Bob Smith",
        age=35,
        city="Boston",
        email="bob@email.com"
    )
    charlie = Person(
        id="charlie-3",
        name="Charlie Brown",
        age=42,
        city="New York",
        email="charlie@email.com"
    )
    diana = Person(
        id="diana-4",
        name="Diana Prince",
        age=31,
        city="San Francisco",
        email="diana@email.com"
    )
    eve = Person(
        id="eve-5",
        name="Eve Wilson",
        age=26,
        city="Boston",
        email="eve@email.com"
    )

    # Create companies
    techcorp = Company(
        id="techcorp-1",
        name="TechCorp",
        industry="Technology",
        founded_year=2010,
        revenue=5000000.0
    )
    finance_inc = Company(
        id="finance-2",
        name="Finance Inc",
        industry="Finance",
        founded_year=2005,
        revenue=10000000.0
    )
    startup_xyz = Company(
        id="startup-3",
        name="StartupXYZ",
        industry="Technology",
        founded_year=2020,
        revenue=1000000.0
    )

    # Create skills
    python_skill = Skill(
        id="python-1",
        name="Python",
        category="Programming",
        difficulty_level=3
    )
    java_skill = Skill(
        id="java-2",
        name="Java",
        category="Programming",
        difficulty_level=4
    )
    sql_skill = Skill(
        id="sql-3",
        name="SQL",
        category="Database",
        difficulty_level=2
    )
    ml_skill = Skill(
        id="ml-4",
        name="Machine Learning",
        category="AI",
        difficulty_level=5
    )

    # Add nodes to graph
    await graph.create_node(alice)
    await graph.create_node(bob)
    await graph.create_node(charlie)
    await graph.create_node(diana)
    await graph.create_node(eve)

    await graph.create_node(techcorp)
    await graph.create_node(finance_inc)
    await graph.create_node(startup_xyz)

    await graph.create_node(python_skill)
    await graph.create_node(java_skill)
    await graph.create_node(sql_skill)
    await graph.create_node(ml_skill)

    # Create relationships
    alice_works = WorksFor(
        id="alice-works-1",
        start_node_id=alice.id,
        end_node_id=techcorp.id,
        position="Senior Developer",
        salary=120000,
        start_date="2022-01-15"
    )
    bob_works = WorksFor(
        id="bob-works-2",
        start_node_id=bob.id,
        end_node_id=techcorp.id,
        position="Manager",
        salary=150000,
        start_date="2018-03-10"
    )
    charlie_works = WorksFor(
        id="charlie-works-3",
        start_node_id=charlie.id,
        end_node_id=finance_inc.id,
        position="Director",
        salary=200000,
        start_date="2015-06-20"
    )
    diana_works = WorksFor(
        id="diana-works-4",
        start_node_id=diana.id,
        end_node_id=startup_xyz.id,
        position="Developer",
        salary=95000,
        start_date="2023-02-01"
    )
    eve_works = WorksFor(
        id="eve-works-5",
        start_node_id=eve.id,
        end_node_id=techcorp.id,
        position="Intern",
        salary=45000,
        start_date="2024-01-15"
    )

    # Add relationships
    await graph.create_relationship(alice_works)
    await graph.create_relationship(bob_works)
    await graph.create_relationship(charlie_works)
    await graph.create_relationship(diana_works)
    await graph.create_relationship(eve_works)

    # Add skills
    alice_python = HasSkill(
        id="alice-python-1",
        start_node_id=alice.id,
        end_node_id=python_skill.id,
        proficiency_level=4,
        years_experience=3
    )
    alice_java = HasSkill(
        id="alice-java-2",
        start_node_id=alice.id,
        end_node_id=java_skill.id,
        proficiency_level=3,
        years_experience=2
    )
    bob_python = HasSkill(
        id="bob-python-3",
        start_node_id=bob.id,
        end_node_id=python_skill.id,
        proficiency_level=5,
        years_experience=5
    )
    bob_sql = HasSkill(
        id="bob-sql-4",
        start_node_id=bob.id,
        end_node_id=sql_skill.id,
        proficiency_level=4,
        years_experience=4
    )
    charlie_ml = HasSkill(
        id="charlie-ml-5",
        start_node_id=charlie.id,
        end_node_id=ml_skill.id,
        proficiency_level=5,
        years_experience=8
    )
    diana_python = HasSkill(
        id="diana-python-6",
        start_node_id=diana.id,
        end_node_id=python_skill.id,
        proficiency_level=3,
        years_experience=1
    )
    eve_java = HasSkill(
        id="eve-java-7",
        start_node_id=eve.id,
        end_node_id=java_skill.id,
        proficiency_level=2,
        years_experience=1
    )

    await graph.create_relationship(alice_python)
    await graph.create_relationship(alice_java)
    await graph.create_relationship(bob_python)
    await graph.create_relationship(bob_sql)
    await graph.create_relationship(charlie_ml)
    await graph.create_relationship(diana_python)
    await graph.create_relationship(eve_java)

    # Add some "knows" relationships
    alice_knows_bob = Knows(
        id="alice-knows-bob-1",
        start_node_id=alice.id,
        end_node_id=bob.id,
        relationship_type="colleague"
    )
    bob_knows_charlie = Knows(
        id="bob-knows-charlie-2",
        start_node_id=bob.id,
        end_node_id=charlie.id,
        relationship_type="mentor"
    )
    diana_knows_eve = Knows(
        id="diana-knows-eve-3",
        start_node_id=diana.id,
        end_node_id=eve.id,
        relationship_type="friend"
    )

    await graph.create_relationship(alice_knows_bob)
    await graph.create_relationship(bob_knows_charlie)
    await graph.create_relationship(diana_knows_eve)

    print("   Sample data created successfully!")


if __name__ == "__main__":
    asyncio.run(demonstrate_linq_style_querying())
