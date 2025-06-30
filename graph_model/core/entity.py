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

"""Base entity interface for all graph model entities."""

from typing import Protocol
from uuid import uuid4


class IEntity(Protocol):
    """
    Protocol defining the foundation for all entities in the graph model.

    This is the base interface for both nodes and relationships, providing
    core identity functionality. All graph entities must have a unique
    identifier that remains immutable after persistence.
    """

    @property
    def id(self) -> str:
        """
        Gets the unique identifier of the entity.

        Identifiers should be immutable once the entity has been persisted
        to ensure referential integrity.

        Returns:
            The unique identifier as a string.
        """
        ...


def generate_entity_id() -> str:
    """
    Generate a new unique entity ID.

    Uses UUID4 without hyphens for consistency with the .NET implementation.

    Returns:
        A new unique identifier string.
    """
    return uuid4().hex
