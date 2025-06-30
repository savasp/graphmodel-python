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
Detailed implementation examples for embedded vs related properties.

This shows how our Python graph model library would actually handle
different storage strategies for complex properties.
"""

import asyncio
import json
from dataclasses import dataclass
from typing import List, Optional

from graph_model import Node, node
from graph_model.attributes.fields import (
    embedded_field,
    property_field,
    related_node_field,
)
from graph_model.providers.neo4j import Neo4jDriver, Neo4jGraph


@dataclass
class ContactInfo:
    email: str
    phone: Optional[str] = None
    city: str = ""


@dataclass
class Address:
    street: str
    city: str
    state: str
    country: str
    zip_code: str


# ============================================================================
# APPROACH 1: EMBEDDED AS JSON STRING (with APOC support)
# ============================================================================

@node("PersonJsonEmbedded")
class PersonJsonEmbedded(Node):
    first_name: str = property_field(index=True)
    last_name: str = property_field(index=True)

    # Stored as JSON string: '{"email":"john@...", "phone":null, "city":"Portland"}'
    contact_info: ContactInfo = embedded_field(storage="json")
    tags: List[str] = embedded_field(storage="json", default_factory=list)


# ============================================================================
# APPROACH 2: EMBEDDED AS FLATTENED PROPERTIES
# ============================================================================

@node("PersonFlattened")
class PersonFlattened(Node):
    first_name: str = property_field(index=True)
    last_name: str = property_field(index=True)

    # Flattened: contact_info_email, contact_info_phone, contact_info_city
    contact_info: ContactInfo = embedded_field(storage="flattened")
    tags: List[str] = embedded_field(storage="array")  # Native Cypher array


# ============================================================================
# APPROACH 3: EMBEDDED AS CYPHER MAP (limited querying)
# ============================================================================

@node("PersonMapEmbedded")
class PersonMapEmbedded(Node):
    first_name: str = property_field(index=True)
    last_name: str = property_field(index=True)

    # Stored as Cypher map: {email: "john@...", phone: null, city: "Portland"}
    contact_info: ContactInfo = embedded_field(storage="map")
    tags: List[str] = embedded_field(storage="array")


# ============================================================================
# APPROACH 4: RELATED NODES (full graph capabilities)
# ============================================================================

@node("PersonRelated")
class PersonRelated(Node):
    first_name: str = property_field(index=True)
    last_name: str = property_field(index=True)

    # Stored as separate ContactInfo and Address nodes
    contact_info: Optional[ContactInfo] = related_node_field(
        relationship_type="HAS_CONTACT_INFO",
        private=True,  # Not discoverable in normal graph traversal
        required=False,
        default=None
    )

    addresses: List[Address] = related_node_field(
        relationship_type="HAS_ADDRESS",
        private=False,  # Discoverable in graph traversal
        default_factory=list
    )


async def demonstrate_storage_implementations():
    """
    Show how different storage approaches would work in practice.
    """

    print("=== STORAGE IMPLEMENTATION COMPARISON ===\n")

    # Initialize Neo4j driver
    print("1. INITIALIZING NEO4J DRIVER")
    await Neo4jDriver.initialize(
        uri="neo4j://localhost:7687",
        user="neo4j",
        password="password",
        database="EmbeddedVsRelatedExamples"
    )
    await Neo4jDriver.ensure_database_exists()
    Neo4jGraph()
    print("   ✓ Driver initialized\n")

    # Sample data
    contact = ContactInfo(email="john@example.com", phone="555-1234", city="Portland")
    tags = ["engineer", "python", "neo4j"]

    print("2. CREATING SAMPLE DATA")

    # Create people with different storage approaches
    john_json = PersonJsonEmbedded(
        id="john-json-1",
        first_name="John",
        last_name="Doe",
        contact_info=contact,
        tags=tags
    )

    jane_flattened = PersonFlattened(
        id="jane-flattened-2",
        first_name="Jane",
        last_name="Smith",
        contact_info=ContactInfo(email="jane@example.com", city="Seattle"),
        tags=["developer", "java"]
    )

    bob_map = PersonMapEmbedded(
        id="bob-map-3",
        first_name="Bob",
        last_name="Johnson",
        contact_info=ContactInfo(email="bob@example.com", phone="555-5678", city="Austin"),
        tags=["manager", "leadership"]
    )

    alice_related = PersonRelated(
        id="alice-related-4",
        first_name="Alice",
        last_name="Brown",
        contact_info=ContactInfo(email="alice@example.com", city="Boston"),
        addresses=[
            Address("123 Home St", "Boston", "MA", "USA", "02101"),
            Address("456 Work Ave", "Cambridge", "MA", "USA", "02139")
        ]
    )

    print(f"   Created John (JSON embedded): {john_json.first_name} {john_json.last_name}")
    print(f"   Created Jane (Flattened): {jane_flattened.first_name} {jane_flattened.last_name}")
    print(f"   Created Bob (Map embedded): {bob_map.first_name} {bob_map.last_name}")
    print(f"   Created Alice (Related nodes): {alice_related.first_name} {alice_related.last_name}")

    # ========================================================================
    # JSON STRING STORAGE
    # ========================================================================
    print("\n3. JSON STRING STORAGE ANALYSIS")
    print("   Person: John Doe")
    print("   Storage: JSON string on node")

    contact_json = json.dumps(contact.__dict__)
    tags_json = json.dumps(tags)
    print(f"   Contact info JSON: {contact_json}")
    print(f"   Tags JSON: {tags_json}")

    print("   Cypher that would be generated:")
    print(f"""
    CREATE (p:PersonJsonEmbedded {{
        first_name: "John",
        last_name: "Doe",
        contact_info: '{contact_json}',
        tags: '{tags_json}'
    }})
    """)

    print("   Query for people in Portland:")
    print("""
    MATCH (p:PersonJsonEmbedded)
    WHERE apoc.json.path(p.contact_info, '$.city') = "Portland"
    RETURN p
    """)
    print("   Pros: Preserves exact object structure")
    print("   Cons: Requires APOC, limited indexing\n")

    # ========================================================================
    # FLATTENED PROPERTIES STORAGE
    # ========================================================================
    print("4. FLATTENED PROPERTIES STORAGE ANALYSIS")
    print("   Person: Jane Smith")
    print("   Storage: Flattened properties on node")

    print("   Cypher that would be generated:")
    print("""
    CREATE (p:PersonFlattened {
        first_name: "Jane",
        last_name: "Smith",
        contact_info_email: "jane@example.com",
        contact_info_phone: null,
        contact_info_city: "Seattle",
        tags: ["developer", "java"]
    })
    """)

    print("   Query for people in Seattle:")
    print("""
    MATCH (p:PersonFlattened)
    WHERE p.contact_info_city = "Seattle"
    RETURN p
    """)
    print("   Pros: Standard Cypher, can index individual fields")
    print("   Cons: Property explosion, loses object structure\n")

    # ========================================================================
    # CYPHER MAP STORAGE
    # ========================================================================
    print("5. CYPHER MAP STORAGE ANALYSIS")
    print("   Person: Bob Johnson")
    print("   Storage: Cypher map on node")

    print("   Cypher that would be generated:")
    print("""
    CREATE (p:PersonMapEmbedded {
        first_name: "Bob",
        last_name: "Johnson",
        contact_info: {
            email: "bob@example.com",
            phone: "555-5678",
            city: "Austin"
        },
        tags: ["manager", "leadership"]
    })
    """)

    print("   Query for people in Austin (LIMITED):")
    print("""
    MATCH (p:PersonMapEmbedded)
    WHERE p.contact_info.city = "Austin"  // This may NOT work!
    RETURN p

    // Safer approach:
    MATCH (p:PersonMapEmbedded)
    WHERE p.contact_info['city'] = "Austin"  // May work in some cases
    RETURN p
    """)
    print("   Pros: Preserves structure, no APOC needed")
    print("   Cons: Very limited querying capabilities\n")

    # ========================================================================
    # RELATED NODES STORAGE
    # ========================================================================
    print("6. RELATED NODES STORAGE ANALYSIS")
    print("   Person: Alice Brown")
    print("   Storage: Separate nodes with relationships")

    print("   Cypher that would be generated:")
    print("""
    CREATE (p:PersonRelated {first_name: "Alice", last_name: "Brown"})
    CREATE (c:ContactInfo {
        email: "alice@example.com",
        phone: null,
        city: "Boston"
    })
    CREATE (a1:Address {
        street: "123 Home St",
        city: "Boston",
        state: "MA",
        country: "USA",
        zip_code: "02101"
    })
    CREATE (a2:Address {
        street: "456 Work Ave",
        city: "Cambridge",
        state: "MA",
        country: "USA",
        zip_code: "02139"
    })
    CREATE (p)-[:HAS_CONTACT_INFO]->(c)
    CREATE (p)-[:HAS_ADDRESS]->(a1)
    CREATE (p)-[:HAS_ADDRESS]->(a2)
    """)

    print("   Query for people in Boston:")
    print("""
    MATCH (p:PersonRelated)-[:HAS_CONTACT_INFO]->(c:ContactInfo)
    WHERE c.city = "Boston"
    RETURN p
    """)
    print("   Pros: Full Cypher power, indexing, relationships")
    print("   Cons: More complex queries, relationship overhead\n")

    # ========================================================================
    # COMPARISON SUMMARY
    # ========================================================================
    print("7. STORAGE STRATEGY COMPARISON")
    print("   JSON String (John):")
    print("   - Contact info: JSON string on node")
    print("   - Querying: Requires APOC functions")
    print("   - Indexing: Limited to full-text search")
    print("   - Performance: Good for reads, slow for complex queries")

    print("\n   Flattened Properties (Jane):")
    print("   - Contact info: contact_info_email, contact_info_city, etc.")
    print("   - Querying: Standard Cypher property access")
    print("   - Indexing: Full indexing on individual fields")
    print("   - Performance: Excellent for simple queries")

    print("\n   Cypher Map (Bob):")
    print("   - Contact info: Native Cypher map object")
    print("   - Querying: Limited map property access")
    print("   - Indexing: No indexing on map properties")
    print("   - Performance: Good for storage, poor for querying")

    print("\n   Related Nodes (Alice):")
    print("   - Contact info: Separate ContactInfo node")
    print("   - Querying: Full graph traversal capabilities")
    print("   - Indexing: Full indexing on related nodes")
    print("   - Performance: Excellent for complex queries and analytics")

    print("\n=== STORAGE IMPLEMENTATION DEMONSTRATION COMPLETE ===")


if __name__ == "__main__":
    asyncio.run(demonstrate_storage_implementations())
