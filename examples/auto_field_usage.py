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
Example demonstrating auto_field usage for automatic field type detection.

This shows how developers can avoid explicit related_node_field declarations
by using auto_field, which automatically determines the appropriate storage strategy.
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from graph_model import Node, Relationship, node, relationship
from graph_model.attributes.fields import auto_field, property_field, related_node_field
from graph_model.providers.neo4j import Neo4jDriver, Neo4jGraph


@dataclass
class Address:
    """A complex type that will be stored as a related node."""
    street: str
    city: str
    state: str
    country: str
    zip_code: str
    created_date: Optional[datetime] = None


@dataclass
class ContactInfo:
    """Another complex type for demonstration."""
    email: str
    phone: Optional[str] = None
    city: str = ""
    preferences: Optional[Dict[str, Any]] = None


@dataclass
class Skill:
    """A complex type representing a skill."""
    name: str
    level: int
    years_experience: int
    certifications: Optional[List[str]] = None


# ============================================================================
# APPROACH 1: Using auto_field (Recommended for most cases)
# ============================================================================

@node("Person")
class Person(Node):
    """
    Person entity using auto_field for automatic field type detection.

    auto_field automatically chooses the appropriate storage strategy:
    - Simple types → property_field (stored directly on node)
    - Complex types → related_node_field (stored as separate nodes)
    - Collections → related_node_field (stored as separate nodes)
    """

    # Simple types - automatically use property_field
    name: str = auto_field(index=True)
    age: int = auto_field(default=0)
    email: str = auto_field()
    is_active: bool = auto_field(default=True)
    created_date: datetime = auto_field(default_factory=datetime.utcnow)

    # Simple collections - automatically use property_field
    tags: List[str] = auto_field(default_factory=list)
    scores: List[float] = auto_field(default_factory=list)

    # Complex types - automatically use related_node_field
    home_address: Address = auto_field()
    work_address: Optional[Address] = auto_field(required=False)
    contact_info: ContactInfo = auto_field()

    # Complex collections - automatically use related_node_field
    skills: List[Skill] = auto_field(default_factory=list)
    previous_addresses: List[Address] = auto_field(default_factory=list)

    # Force embedded storage for specific complex types
    metadata: Dict[str, Any] = auto_field(prefer_embedded=True, default_factory=dict)


# ============================================================================
# APPROACH 2: Explicit field types (For fine-grained control)
# ============================================================================

@node("PersonExplicit")
class PersonExplicit(Node):
    """
    Person entity using explicit field types for maximum control.

    This approach gives you complete control over storage strategies
    but requires more explicit declarations.
    """

    # Simple properties - explicit property_field
    name: str = property_field(index=True)
    age: int = property_field(default=0)
    email: str = property_field()

    # Simple collections - explicit property_field
    tags: List[str] = property_field(default_factory=list)

    # Complex properties - explicit related_node_field with .NET convention
    home_address: Address = related_node_field()  # Uses "__PROPERTY__home_address__"
    work_address: Address = related_node_field()  # Uses "__PROPERTY__work_address__"

    # Custom relationship types
    contact_info: ContactInfo = related_node_field(
        relationship_type="HAS_CONTACT_INFO",
        private=False
    )

    # Complex collections - explicit related_node_field
    skills: List[Skill] = related_node_field(
        relationship_type="HAS_SKILL",
        private=False,
        default_factory=list
    )

    # Embedded storage for specific cases
    metadata: Dict[str, Any] = property_field(default_factory=dict)  # Simple dict


# ============================================================================
# APPROACH 3: Mixed approach (Best of both worlds)
# ============================================================================

@node("PersonMixed")
class PersonMixed(Node):
    """
    Person entity using a mixed approach.

    Use auto_field for most cases, but override with explicit types
    when you need specific control.
    """

    # Use auto_field for most properties
    name: str = auto_field(index=True)
    age: int = auto_field(default=0)
    home_address: Address = auto_field()
    skills: List[Skill] = auto_field(default_factory=list)

    # Override with explicit types when needed
    work_address: Address = related_node_field(
        relationship_type="WORKS_AT",  # Custom relationship type
        private=False  # Public relationship for graph traversal
    )

    # Force embedded storage for performance-critical data
    quick_metadata: Dict[str, Any] = property_field(default_factory=dict)


# ============================================================================
# RELATIONSHIP EXAMPLE
# ============================================================================

@relationship("KNOWS")
class Knows(Relationship):
    """Relationship between people."""

    # Simple properties on relationships
    since: datetime = auto_field(default_factory=datetime.utcnow)
    strength: float = auto_field(default=1.0)

    # Note: Relationships typically don't have complex properties
    # in most graph databases, so auto_field will use property_field


async def demonstrate_auto_field_benefits():
    """Show the benefits of using auto_field by creating and using objects."""

    print("=== AUTO_FIELD BENEFITS DEMONSTRATION ===\n")

    # Initialize Neo4j driver (similar to basic_usage.py)
    print("1. INITIALIZING NEO4J DRIVER")
    await Neo4jDriver.initialize(
        uri="neo4j://localhost:7687",
        user="neo4j",
        password="password",
        database="AutoFieldExamples"
    )
    await Neo4jDriver.ensure_database_exists()
    Neo4jGraph()
    print("   ✓ Driver initialized\n")

    # Create sample data
    print("2. CREATING SAMPLE DATA")

    # Create addresses
    home_addr = Address(
        street="123 Main St",
        city="Portland",
        state="OR",
        country="USA",
        zip_code="97201",
        created_date=datetime.utcnow()
    )

    work_addr = Address(
        street="456 Business Ave",
        city="Portland",
        state="OR",
        country="USA",
        zip_code="97205",
        created_date=datetime.utcnow()
    )

    # Create skills
    python_skill = Skill("Python", 5, 3, ["Python Certified"])
    java_skill = Skill("Java", 4, 2, ["Oracle Certified"])
    ml_skill = Skill("Machine Learning", 3, 1, [])

    # Create person using auto_field (Approach 1)
    alice = Person(
        id="alice-auto-123",
        name="Alice Johnson",
        age=30,
        email="alice@example.com",
        is_active=True,
        tags=["developer", "python", "senior"],
        scores=[95.5, 87.2, 92.1],
        home_address=home_addr,
        work_address=work_addr,
        contact_info=ContactInfo(
            email="alice@example.com",
            phone="555-0101",
            city="Portland",
            preferences={"theme": "dark", "notifications": True}
        ),
        skills=[python_skill, java_skill, ml_skill],
        previous_addresses=[
            Address("100 Old St", "Seattle", "WA", "USA", "98101"),
            Address("200 Previous Ave", "Austin", "TX", "USA", "73301")
        ],
        metadata={"department": "engineering", "level": "senior"}
    )

    print(f"   Created Alice using auto_field: {alice.name}")
    print(f"   Simple properties: age={alice.age}, email={alice.email}")
    print(f"   Simple collections: tags={alice.tags}, scores={alice.scores}")
    print(f"   Complex properties: home_address={alice.home_address.city}")
    print(f"   Complex collections: {len(alice.skills)} skills")
    print(f"   Embedded metadata: {alice.metadata}")

    # Create person using explicit fields (Approach 2)
    bob = PersonExplicit(
        id="bob-explicit-456",
        name="Bob Smith",
        age=28,
        email="bob@example.com",
        tags=["developer", "java"],
        home_address=Address("789 Oak St", "Seattle", "WA", "USA", "98102"),
        work_address=Address("321 Tech Blvd", "Seattle", "WA", "USA", "98103"),
        contact_info=ContactInfo(
            email="bob@example.com",
            phone="555-0202",
            city="Seattle"
        ),
        skills=[java_skill],
        metadata={"department": "engineering", "level": "mid"}
    )

    print(f"\n   Created Bob using explicit fields: {bob.name}")
    print("   Custom relationship types will be used for contact_info and skills")

    # Create person using mixed approach (Approach 3)
    charlie = PersonMixed(
        id="charlie-mixed-789",
        name="Charlie Brown",
        age=35,
        home_address=Address("654 Pine St", "Austin", "TX", "USA", "73301"),
        skills=[python_skill, ml_skill],
        work_address=Address("987 Innovation Dr", "Austin", "TX", "USA", "73302"),
        quick_metadata={"department": "ai", "level": "lead"}
    )

    print(f"\n   Created Charlie using mixed approach: {charlie.name}")
    print("   Custom relationship type 'WORKS_AT' for work_address")

    # Create relationships
    print("\n3. CREATING RELATIONSHIPS")

    Knows(
        id="alice-knows-bob",
        start_node_id=alice.id,
        end_node_id=bob.id,
        since=datetime.utcnow(),
        strength=0.8
    )

    Knows(
        id="bob-knows-charlie",
        start_node_id=bob.id,
        end_node_id=charlie.id,
        since=datetime.utcnow(),
        strength=0.6
    )

    print(f"   Created relationship: {alice.name} knows {bob.name}")
    print(f"   Created relationship: {bob.name} knows {charlie.name}")

    # Demonstrate field type detection
    print("\n4. FIELD TYPE DETECTION ANALYSIS")

    # Check what types of fields were created
    print("   Alice (auto_field approach):")
    print("   - Simple types (name, age, email) → stored as node properties")
    print("   - Simple collections (tags, scores) → stored as node properties")
    print("   - Complex types (home_address, contact_info) → stored as related nodes")
    print("   - Complex collections (skills, previous_addresses) → stored as related nodes")
    print("   - Embedded metadata → stored as JSON on node")

    print("\n   Bob (explicit approach):")
    print("   - All field types explicitly declared")
    print("   - Custom relationship types for contact_info and skills")

    print("\n   Charlie (mixed approach):")
    print("   - Most fields use auto_field")
    print("   - work_address uses custom 'WORKS_AT' relationship type")

    # Demonstrate .NET compatibility
    print("\n5. .NET COMPATIBILITY")
    print("   Relationship types that will be created:")
    print("   - __PROPERTY__home_address__ (auto_field)")
    print("   - __PROPERTY__contact_info__ (auto_field)")
    print("   - __PROPERTY__skills__ (auto_field)")
    print("   - HAS_CONTACT_INFO (explicit)")
    print("   - HAS_SKILL (explicit)")
    print("   - WORKS_AT (mixed approach)")

    # Show the benefits
    print("\n6. AUTO_FIELD BENEFITS DEMONSTRATED")
    print("   ✓ Automatic type detection - no need to remember field types")
    print("   ✓ .NET compatibility - uses '__PROPERTY__{fieldName}__' convention")
    print("   ✓ Reduced boilerplate - less explicit field declarations")
    print("   ✓ Type safety - still provides full type checking")
    print("   ✓ Flexibility - can override with explicit types when needed")

    print("\n=== AUTO_FIELD DEMONSTRATION COMPLETE ===")


if __name__ == "__main__":
    asyncio.run(demonstrate_auto_field_benefits())
