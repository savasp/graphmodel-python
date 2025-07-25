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

"""Attributes and decorators for configuring graph model entities."""

from .annotations import Default, Indexed, Required
from .decorators import node, relationship
from .fields import embedded_field, property_field, related_node_field

__all__ = [
    # Decorators
    "node",
    "relationship",

    # Field types
    "property_field",
    "embedded_field",
    "related_node_field",

    # Annotation classes
    "Default",
    "Indexed",
    "Required",
]
