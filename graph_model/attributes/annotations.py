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
Annotation-based configuration for graph model fields.

This module provides annotation classes that can be used with typing.Annotated
to configure field behavior in graph models.
"""

from typing import Any, Generic, TypeVar

T = TypeVar('T')


class Indexed:
    """Mark a field for indexing in the graph database."""
    pass


class Required:
    """Mark a field as required (non-nullable)."""
    pass


class Default(Generic[T]):
    """Provide a default value for a field."""
    
    def __init__(self, value: T):
        self.value = value 