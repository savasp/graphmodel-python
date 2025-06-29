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

"""Node interfaces and base implementations."""

from typing import Protocol

from pydantic import BaseModel, Field

from .entity import IEntity, generate_entity_id


class INode(IEntity, Protocol):
    """
    Protocol defining the contract for node entities in the graph model.
    
    Nodes represent primary data entities that can be connected via relationships.
    This interface serves as a marker interface that extends IEntity,
    signifying that implementing classes represent nodes rather than relationships.
    """

    pass  # Marker interface - no additional members beyond IEntity


class Node(BaseModel):
    """
    Base class for graph nodes that provides a default implementation of the INode interface.
    
    This serves as a foundation for creating domain-specific node entities with
    automatic ID generation and basic node functionality.
    """

    id: str = Field(default_factory=generate_entity_id, frozen=True)
    """The unique identifier of this node."""

    model_config = {
        "validate_assignment": True,
        "use_enum_values": True
    } 