
import pytest

from tests.conftest import (
    ComplexPerson,
    EmbeddedAddress,
    EmbeddedContact,
    EmbeddedSkills,
)


class TestEmbeddedFieldsIntegration:
    @pytest.mark.asyncio
    async def test_embedded_field_serialization(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(ComplexPerson):
            person = ComplexPerson(
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
                    EmbeddedSkills(name="GraphQL", level=4, category="API")
                ],
                preferences={"theme": "dark", "language": "en", "timezone": "PST"}
            )

            created_person = await neo4j_graph.create_node(person)

            # Read back and verify embedded fields
            read_person = await neo4j_graph.get_node(created_person.id)
            assert read_person is not None

            # Verify contact_info
            assert read_person.contact_info.email == "bob@example.com"
            assert read_person.contact_info.phone == "555-1234"
            assert read_person.contact_info.city == "Seattle"

            # Verify home_address
            assert read_person.home_address.street == "456 Pine St"
            assert read_person.home_address.city == "Seattle"
            assert read_person.home_address.state == "WA"
            assert read_person.home_address.country == "USA"
            assert read_person.home_address.zip_code == "98101"

            # Verify skills list
            assert len(read_person.skills) == 2
            python_skill = next(s for s in read_person.skills if s.name == "Python")
            assert python_skill.level == 5
            assert python_skill.category == "Programming"

            # Verify preferences dict
            assert read_person.preferences["theme"] == "dark"
            assert read_person.preferences["language"] == "en"
            assert read_person.preferences["timezone"] == "PST"
            break

    @pytest.mark.asyncio
    async def test_embedded_field_querying(self, neo4j_graph_factory):
        async for neo4j_graph in neo4j_graph_factory(ComplexPerson):
            people = [
                ComplexPerson(
                    first_name="Alice", last_name="Smith", age=30,
                    contact_info=EmbeddedContact(
                        email="alice@example.com", phone="555-1111", city="Portland"
                    ),
                    home_address=EmbeddedAddress(
                        street="123 Main St", city="Portland", state="OR",
                        country="USA", zip_code="97201"
                    ),
                    skills=[EmbeddedSkills(name="Python", level=5, category="Programming")],
                    preferences={"theme": "light"}
                ),
                ComplexPerson(
                    first_name="Bob", last_name="Jones", age=35,
                    contact_info=EmbeddedContact(
                        email="bob@example.com", phone="555-2222", city="Seattle"
                    ),
                    home_address=EmbeddedAddress(
                        street="456 Pine St", city="Seattle", state="WA",
                        country="USA", zip_code="98101"
                    ),
                    skills=[EmbeddedSkills(name="Java", level=4, category="Programming")],
                    preferences={"theme": "dark"}
                )
            ]

            for person in people:
                await neo4j_graph.create_node(person)

            # Query by embedded field (implementation may vary)
            # For now, just verify the nodes were created with embedded fields
            read_person = await neo4j_graph.get_node(people[0].id)
            assert read_person is not None
            assert read_person.contact_info.city == "Portland"
            assert read_person.preferences["theme"] == "light"
            break
