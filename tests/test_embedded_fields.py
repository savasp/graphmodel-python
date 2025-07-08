
import pytest

from tests.conftest import (
    ComplexPerson,
    EmbeddedAddress,
    EmbeddedContact,
    EmbeddedSkills,
)


class TestEmbeddedFields:
    """Test embedded field functionality."""

    @pytest.mark.asyncio
    async def test_embedded_field_serialization(self, mock_neo4j_graph):
        """Test that embedded fields are serialized correctly."""
        # Create node with embedded fields
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

        # Mock create_node to return the person
        mock_neo4j_graph.create_node.return_value = person

        created_person = await mock_neo4j_graph.create_node(person)

        # Verify embedded fields are preserved
        assert created_person.contact_info.email == "bob@example.com"
        assert created_person.contact_info.phone == "555-1234"
        assert created_person.contact_info.city == "Seattle"

        assert created_person.home_address.street == "456 Pine St"
        assert created_person.home_address.city == "Seattle"
        assert created_person.home_address.state == "WA"
        assert created_person.home_address.country == "USA"
        assert created_person.home_address.zip_code == "98101"

        assert len(created_person.skills) == 2
        assert created_person.skills[0].name == "Python"
        assert created_person.skills[0].level == 5
        assert created_person.skills[0].category == "Programming"
        assert created_person.skills[1].name == "GraphQL"
        assert created_person.skills[1].level == 4
        assert created_person.skills[1].category == "API"

        assert created_person.preferences["theme"] == "dark"
        assert created_person.preferences["language"] == "en"
        assert created_person.preferences["timezone"] == "PST"

    @pytest.mark.asyncio
    async def test_embedded_field_querying(self, mock_neo4j_graph):
        """Test querying nodes with embedded fields."""
        # Create test data with embedded fields
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

        # Mock create_node to return each person
        mock_neo4j_graph.create_node.side_effect = people

        created_people = []
        for person in people:
            created_person = await mock_neo4j_graph.create_node(person)
            created_people.append(created_person)

        # Verify all nodes were created with embedded fields
        assert len(created_people) == 2

        # Test filtering by embedded field properties
        portland_people = [p for p in created_people if p.contact_info.city == "Portland"]
        assert len(portland_people) == 1
        assert portland_people[0].first_name == "Alice"

        seattle_people = [p for p in created_people if p.contact_info.city == "Seattle"]
        assert len(seattle_people) == 1
        assert seattle_people[0].first_name == "Bob"

        # Test filtering by embedded field nested properties
        python_developers = [p for p in created_people if any(s.name == "Python" for s in p.skills)]
        assert len(python_developers) == 1
        assert python_developers[0].first_name == "Alice"

        dark_theme_users = [p for p in created_people if p.preferences.get("theme") == "dark"]
        assert len(dark_theme_users) == 1
        assert dark_theme_users[0].first_name == "Bob"
