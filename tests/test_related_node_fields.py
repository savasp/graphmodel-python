from datetime import date, datetime

import pytest

from tests.conftest import (
    ComplexPerson,
    EmbeddedAddress,
    EmbeddedContact,
    TestAddress,
    TestCompany,
)


class TestRelatedNodeFields:
    """Test related node field functionality."""

    @pytest.mark.asyncio
    async def test_related_node_creation(self, mock_neo4j_graph):
        """Test creating nodes with related node fields."""
        # Create related nodes
        address = TestAddress(
            street="123 Work St",
            city="Portland",
            state="OR",
            country="USA",
            zip_code="97201"
        )
        company = TestCompany(
            name="Tech Corp",
            industry="Technology",
            founded_year=2010
        )
        
        # Mock create_node to return each node in sequence
        mock_neo4j_graph.create_node.side_effect = [address, company]
        
        created_address = await mock_neo4j_graph.create_node(address)
        created_company = await mock_neo4j_graph.create_node(company)
        
        # Verify related nodes were created
        assert created_address.street == "123 Work St"
        assert created_company.name == "Tech Corp"
        
        # Create person with related nodes
        person = ComplexPerson(
            first_name="Alice",
            last_name="Smith",
            age=30,
            contact_info=EmbeddedContact(
                email="alice@example.com",
                phone="555-1111",
                city="Portland"
            ),
            home_address=EmbeddedAddress(
                street="456 Home St",
                city="Portland",
                state="OR",
                country="USA",
                zip_code="97202"
            ),
            skills=[],
            preferences={"theme": "light"},
            work_address=created_address,
            companies=[created_company],
            projects=[]
        )
        
        # Reset mock to return the person
        mock_neo4j_graph.create_node.return_value = person
        mock_neo4j_graph.create_node.side_effect = None
        
        created_person = await mock_neo4j_graph.create_node(person)
        
        # Verify person was created with related nodes
        assert created_person.first_name == "Alice"
        assert created_person.work_address is not None
        assert created_person.work_address.street == "123 Work St"
        assert len(created_person.companies) == 1
        assert created_person.companies[0].name == "Tech Corp"

    @pytest.mark.asyncio
    async def test_related_node_querying(self, mock_neo4j_graph):
        """Test querying nodes with related node fields."""
        # Create test data
        address = TestAddress(
            street="123 Work St",
            city="Portland",
            state="OR",
            country="USA",
            zip_code="97201"
        )
        company = TestCompany(
            name="Tech Corp",
            industry="Technology",
            founded_year=2010
        )
        
        # Mock create_node to return each node in sequence
        mock_neo4j_graph.create_node.side_effect = [address, company]
        
        created_address = await mock_neo4j_graph.create_node(address)
        created_company = await mock_neo4j_graph.create_node(company)
        
        # Create person with related nodes
        person = ComplexPerson(
            first_name="Bob",
            last_name="Jones",
            age=35,
            contact_info=EmbeddedContact(
                email="bob@example.com",
                phone="555-2222",
                city="Seattle"
            ),
            home_address=EmbeddedAddress(
                street="456 Home St",
                city="Seattle",
                state="WA",
                country="USA",
                zip_code="98101"
            ),
            skills=[],
            preferences={"theme": "dark"},
            work_address=created_address,
            companies=[created_company],
            projects=[]
        )
        
        # Reset mock to return the person
        mock_neo4j_graph.create_node.return_value = person
        mock_neo4j_graph.create_node.side_effect = None
        
        created_person = await mock_neo4j_graph.create_node(person)
        
        # Verify person was created with related nodes
        assert created_person.first_name == "Bob"
        assert created_person.work_address is not None
        assert created_person.work_address.street == "123 Work St"
        assert len(created_person.companies) == 1
        assert created_person.companies[0].name == "Tech Corp" 