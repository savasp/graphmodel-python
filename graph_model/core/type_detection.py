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
Type detection utilities for graph model fields.

This module provides utilities to determine how fields should be stored
in the graph database based on their type annotations.
"""

import datetime
import decimal
import enum
import uuid
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
)

from ..core.node import Node
from ..core.relationship import Relationship


class FieldStorageType(enum.Enum):
    """Enumeration of field storage types."""
    SIMPLE = "simple"
    COMPLEX = "complex"


class TypeDetector:
    """Utility class for detecting field storage types based on type annotations."""

    @staticmethod
    def is_simple_type(type_hint: Type) -> bool:
        """
        Check if a type is considered "simple" for graph storage.
        
        Follows .NET GraphDataModel.IsSimple() logic for compatibility.
        Simple types can be stored directly as Neo4j properties.
        """
        # Handle None type
        if type_hint is type(None):
            return True

        # Handle Union types (including Optional)
        origin = get_origin(type_hint)
        if origin is Union:
            args = get_args(type_hint)
            # For Optional[T] (Union[T, None]), check if T is simple
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                return TypeDetector.is_simple_type(non_none_args[0])
            # For other unions, consider complex
            return False

        # Basic simple types - matches .NET simple types
        simple_types = {
            str, int, float, bool, bytes,
            datetime.datetime, datetime.date, datetime.time,
            uuid.UUID, decimal.Decimal
        }

        if type_hint in simple_types:
            return True

        # Handle enums
        if hasattr(type_hint, '__bases__') and any(base.__name__ == 'Enum' for base in type_hint.__bases__):
            return True

        # Handle collections of simple types
        if TypeDetector.is_collection_of_simple(type_hint):
            return True

        # Handle dictionaries with simple key/value types
        if TypeDetector.is_simple_dict(type_hint):
            return True

        return False

    @staticmethod
    def is_collection_of_simple(type_hint: Type) -> bool:
        """
        Check if a type is a collection of simple types.
        
        Matches .NET GraphDataModel.IsCollectionOfSimple() for compatibility.
        """
        origin = get_origin(type_hint)
        if origin in (list, List, set, Set, tuple, Tuple):
            args = get_args(type_hint)
            if args:
                return TypeDetector.is_simple_type(args[0])
        return False

    @staticmethod
    def is_simple_dict(type_hint: Type) -> bool:
        """Check if a type is a dictionary with simple key/value types."""
        origin = get_origin(type_hint)
        if origin in (dict, Dict):
            args = get_args(type_hint)
            if len(args) == 2:
                key_type, value_type = args
                return (TypeDetector.is_simple_type(key_type) and 
                       TypeDetector.is_simple_type(value_type))
        return False

    @staticmethod
    def is_complex_type(type_hint: Type, depth: int = 5) -> bool:
        """
        Check if a type is considered "complex" for graph storage.
        
        Follows .NET GraphDataModel.IsComplex() logic with depth checking.
        Complex types need to be stored as separate nodes with relationships.
        """
        if depth <= 0:
            return False

        if TypeDetector.is_simple_type(type_hint):
            return False

        # Handle Optional types
        origin = get_origin(type_hint)
        if origin is Union:
            args = get_args(type_hint)
            non_none_args = [arg for arg in args if arg is not type(None)]
            if len(non_none_args) == 1:
                return TypeDetector.is_complex_type(non_none_args[0], depth - 1)

        # Check if it's a Node or Relationship type (not allowed as properties)
        if TypeDetector.is_node_or_relationship_type(type_hint):
            return False

        # Check if it's a Pydantic model or has complex properties
        if hasattr(type_hint, 'model_fields'):
            # Pydantic model - check its fields
            for _field_name, field_info in type_hint.model_fields.items():
                field_type = field_info.annotation
                if not TypeDetector.is_simple_type(field_type):
                    if TypeDetector.is_complex_type(field_type, depth - 1):
                        return True

        # Check collections of complex types
        if TypeDetector.is_collection_of_complex(type_hint):
            return True

        # Default to complex for any class that's not simple
        return True

    @staticmethod
    def is_collection_of_complex(type_hint: Type) -> bool:
        """
        Check if a type is a collection of complex types.
        
        Matches .NET GraphDataModel.IsCollectionOfComplex() for compatibility.
        """
        origin = get_origin(type_hint)
        if origin in (list, List, set, Set, tuple, Tuple):
            args = get_args(type_hint)
            if args:
                return TypeDetector.is_complex_type(args[0])
        return False

    @staticmethod
    def is_node_or_relationship_type(type_hint: Type) -> bool:
        """Check if a type inherits from Node or Relationship."""
        if hasattr(type_hint, '__bases__'):
            return (Node in type_hint.__mro__ or Relationship in type_hint.__mro__)
        return False

    @staticmethod
    def get_field_storage_type(type_hint: Type) -> FieldStorageType:
        """
        Determine the storage strategy for a field type.
        
        Returns:
            FieldStorageType.SIMPLE for types that can be stored directly
            FieldStorageType.COMPLEX for types that need separate nodes
        """
        if TypeDetector.is_simple_type(type_hint):
            return FieldStorageType.SIMPLE
        else:
            return FieldStorageType.COMPLEX 