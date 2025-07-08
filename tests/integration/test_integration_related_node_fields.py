
import pytest

from tests.conftest import (
    ComplexPerson,
    EmbeddedAddress,
    EmbeddedContact,
    TestAddress,
    TestCompany,
    TestProject,
)


class TestRelatedNodeFieldsIntegration:
    @pytest.mark.asyncio
    async def test_related_node_creation(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(ComplexPerson):
            # Create related nodes first
            address = TestAddress(
                street="789 Work St",
                city="Portland",
                state="OR",
                country="USA",
                zip_code="97202"
            )
            company = TestCompany(
                name="TechCorp",
                industry="Technology",
                founded_year=2010
            )
            project = TestProject(
                name="Graph Database",
                description="Building a graph database system",
                status="active",
                budget=100000.0
            )

            created_address = await neo4j_graph.create_node(address)
            created_company = await neo4j_graph.create_node(company)
            created_project = await neo4j_graph.create_node(project)

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
                    street="123 Main St",
                    city="Portland",
                    state="OR",
                    country="USA",
                    zip_code="97201"
                ),
                skills=[],
                preferences={"theme": "light"},
                work_address=created_address,
                companies=[created_company],
                projects=[created_project]
            )

            created_person = await neo4j_graph.create_node(person)

            assert created_person.id is not None
            assert created_person.work_address is not None
            assert created_person.work_address.id == created_address.id
            assert len(created_person.companies) == 1
            assert created_person.companies[0].id == created_company.id
            assert len(created_person.projects) == 1
            assert created_person.projects[0].id == created_project.id
            break

    @pytest.mark.asyncio
    async def test_related_node_querying(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(ComplexPerson):
            address1 = TestAddress(
                street="123 Main St", city="Portland", state="OR",
                country="USA", zip_code="97201"
            )
            address2 = TestAddress(
                street="456 Pine St", city="Seattle", state="WA",
                country="USA", zip_code="98101"
            )

            company1 = TestCompany(
                name="TechCorp", industry="Technology", founded_year=2010
            )
            company2 = TestCompany(
                name="DataCorp", industry="Data", founded_year=2015
            )

            created_address1 = await neo4j_graph.create_node(address1)
            created_address2 = await neo4j_graph.create_node(address2)
            created_company1 = await neo4j_graph.create_node(company1)
            created_company2 = await neo4j_graph.create_node(company2)

            person1 = ComplexPerson(
                first_name="Alice", last_name="Smith", age=30,
                contact_info=EmbeddedContact(email="alice@example.com", city="Portland"),
                home_address=EmbeddedAddress(street="123 Main St", city="Portland", state="OR", country="USA", zip_code="97201"),
                skills=[], preferences={},
                work_address=created_address1,
                companies=[created_company1],
                projects=[]
            )

            person2 = ComplexPerson(
                first_name="Bob", last_name="Jones", age=35,
                contact_info=EmbeddedContact(email="bob@example.com", city="Seattle"),
                home_address=EmbeddedAddress(street="456 Pine St", city="Seattle", state="WA", country="USA", zip_code="98101"),
                skills=[], preferences={},
                work_address=created_address2,
                companies=[created_company1, created_company2],
                projects=[]
            )

            await neo4j_graph.create_node(person1)
            await neo4j_graph.create_node(person2)

            read_person1 = await neo4j_graph.get_node(person1.id)
            read_person2 = await neo4j_graph.get_node(person2.id)

            assert read_person1 is not None
            assert read_person2 is not None
            assert read_person1.work_address is not None
            assert read_person2.work_address is not None
            break
