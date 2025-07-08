from datetime import date, datetime
from typing import Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from pydantic import BaseModel

from graph_model import Node, Relationship, node, property_field, relationship
from graph_model.attributes.fields import embedded_field, related_node_field
from graph_model.core.relationship import RelationshipDirection
from graph_model.providers.neo4j import Neo4jDriver, Neo4jGraph

# Configure pytest-asyncio to use the same event loop for all tests
pytest_plugins = ('pytest_asyncio',)

# Node models
def _models():
    @node(label="TestPerson")
    class TestPerson(Node):
        __test__ = False
        first_name: str = property_field(index=True)
        last_name: str = property_field(index=True)
        age: int = property_field()
        email: str = property_field()
        is_active: bool = property_field()
        score: float = property_field()
        tags: List[str] = property_field()
        metadata: Dict[str, str] = property_field()
        created_at: datetime = property_field()
        birth_date: date = property_field()

    @node(label="TestAddress")
    class TestAddress(Node):
        __test__ = False
        street: str = property_field()
        city: str = property_field()
        state: str = property_field()
        country: str = property_field()
        zip_code: str = property_field()

    @node(label="TestContact")
    class TestContact(Node):
        __test__ = False
        email: str = property_field()
        phone: Optional[str] = property_field()
        city: str = property_field()

    @node(label="TestCompany")
    class TestCompany(Node):
        __test__ = False
        name: str = property_field()
        industry: str = property_field()
        founded_year: int = property_field()

    @node(label="TestProject")
    class TestProject(Node):
        __test__ = False
        name: str = property_field()
        description: str = property_field()
        status: str = property_field()
        budget: float = property_field()

    class EmbeddedAddress(BaseModel):
        street: str
        city: str
        state: str
        country: str
        zip_code: str

    class EmbeddedContact(BaseModel):
        email: str
        phone: Optional[str] = None
        city: str

    class EmbeddedSkills(BaseModel):
        name: str
        level: int
        category: str

    @node(label="ComplexPerson")
    class ComplexPerson(Node):
        __test__ = False
        first_name: str = property_field(index=True)
        last_name: str = property_field(index=True)
        age: int = property_field()
        contact_info: EmbeddedContact = embedded_field()
        home_address: EmbeddedAddress = embedded_field()
        skills: List[EmbeddedSkills] = property_field()
        preferences: Dict[str, str] = property_field()
        work_address: Optional[TestAddress] = related_node_field(
            relationship_type="WORKS_AT",
            private=True,
            required=False,
            default=None
        )
        companies: List[TestCompany] = related_node_field(
            relationship_type="WORKS_FOR",
            private=False,
            required=True,
            default_factory=list
        )
        projects: List[TestProject] = related_node_field(
            relationship_type="MANAGES",
            private=False,
            required=True,
            default_factory=list
        )

    @relationship(label="KNOWS", direction=RelationshipDirection.BIDIRECTIONAL)
    class KnowsRelationship(Relationship):
        __test__ = False
        since: datetime = property_field()
        strength: float = property_field()

    @relationship(label="WORKS_AT", direction=RelationshipDirection.OUTGOING)
    class WorksAtRelationship(Relationship):
        __test__ = False
        position: str = property_field()
        start_date: date = property_field()
        salary: float = property_field()

    @relationship(label="MANAGES", direction=RelationshipDirection.OUTGOING)
    class ManagesRelationship(Relationship):
        __test__ = False
        role: str = property_field()
        authority_level: int = property_field()

    return locals()

MODELS = _models()
TestPerson = MODELS['TestPerson']
TestAddress = MODELS['TestAddress']
TestContact = MODELS['TestContact']
TestCompany = MODELS['TestCompany']
TestProject = MODELS['TestProject']
EmbeddedAddress = MODELS['EmbeddedAddress']
EmbeddedContact = MODELS['EmbeddedContact']
EmbeddedSkills = MODELS['EmbeddedSkills']
ComplexPerson = MODELS['ComplexPerson']
KnowsRelationship = MODELS['KnowsRelationship']
WorksAtRelationship = MODELS['WorksAtRelationship']
ManagesRelationship = MODELS['ManagesRelationship']

@pytest.fixture
def mock_neo4j_graph():
    """Create a mock Neo4j graph for unit tests."""
    graph = MagicMock(spec=Neo4jGraph)
    graph.create_node = AsyncMock()
    graph.get_node = AsyncMock()
    graph.update_node = AsyncMock()
    graph.delete_node = AsyncMock()
    return graph

@pytest_asyncio.fixture(scope="function")
async def neo4j_driver():
    """Initialize Neo4j driver once per function."""
    try:
        print("[DEBUG] Attempting to initialize real Neo4j driver...")
        await Neo4jDriver.initialize(
            uri="neo4j://localhost:7687",
            user="neo4j",
            password="password",
            database="pythontests"
        )
        await Neo4jDriver.ensure_database_exists()
        print("[DEBUG] Real Neo4j driver initialized.")
        yield Neo4jDriver
    except Exception as e:
        print(f"[DEBUG] Exception initializing Neo4j driver: {e}")
        # If Neo4j is not available, create a mock driver
        mock_driver = MagicMock()
        Neo4jDriver._driver = mock_driver
        print("[DEBUG] Using MagicMock for Neo4j driver.")
        yield Neo4jDriver
    finally:
        # Always close the driver to avoid event loop issues
        await Neo4jDriver.close()

@pytest_asyncio.fixture(scope="function")
async def neo4j_graph_factory(neo4j_driver):
    """Factory fixture to create a Neo4jGraph with a specific node and relationship type."""
    async def _factory(node_type, relationship_type=None):
        graph = Neo4jGraph(neo4j_driver)
        graph._node_type = node_type
        if relationship_type is not None:
            graph._relationship_type = relationship_type
        # Clean up database before and after each test
        if hasattr(neo4j_driver._driver, 'session'):
            try:
                if hasattr(neo4j_driver._driver, 'execute_query'):
                    await neo4j_driver._driver.execute_query("MATCH (n) DETACH DELETE n")
            except Exception:
                pass
            yield graph
            try:
                if hasattr(neo4j_driver._driver, 'execute_query'):
                    await neo4j_driver._driver.execute_query("MATCH (n) DETACH DELETE n")
            except Exception:
                pass
    return _factory

@pytest.fixture
def sample_person():
    return TestPerson(
        first_name="Alice",
        last_name="Smith",
        age=30,
        email="alice@example.com",
        is_active=True,
        score=95.5,
        tags=["engineer", "python"],
        metadata={"department": "engineering", "level": "senior"},
        created_at=datetime(2023, 1, 15, 10, 30, 0),
        birth_date=date(1993, 5, 20)
    )

@pytest.fixture
def sample_address():
    return TestAddress(
        street="123 Main St",
        city="Portland",
        state="OR",
        country="USA",
        zip_code="97201"
    )

@pytest.fixture
def sample_complex_person():
    return ComplexPerson(
        first_name="Bob",
        last_name="Jones",
        age=35,
        contact_info=EmbeddedContact(
            email="bob@example.com",
            phone="555-1234",
            city="Seattle"
        ),
        home_address=EmbeddedAddress(
            street="456 Pine St",
            city="Seattle",
            state="WA",
            country="USA",
            zip_code="98101"
        ),
        skills=[
            EmbeddedSkills(name="Python", level=5, category="Programming"),
            EmbeddedSkills(name="GraphQL", level=4, category="API"),
            EmbeddedSkills(name="Neo4j", level=3, category="Database")
        ],
        preferences={"theme": "dark", "language": "en", "timezone": "PST"}
    )
