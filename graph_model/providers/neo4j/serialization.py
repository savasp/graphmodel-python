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
Neo4j serialization utilities.

This module provides serialization and deserialization utilities for converting
graph model entities to and from Neo4j format.
"""

import ast
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, Union, get_args, get_origin


@dataclass(frozen=True)
class SerializedNode:
    """Represents a serialized node in Neo4j format."""
    id: str
    labels: List[str]
    properties: Dict[str, Any]
    complex_properties: Dict[str, Any]


@dataclass(frozen=True)
class SerializedRelationship:
    """Represents a serialized relationship in Neo4j format."""
    id: str
    type: str
    start_node_id: str
    end_node_id: str
    properties: Dict[str, Any]
    complex_properties: Dict[str, Any]

from neo4j import Record

from ...core import FieldStorageType, ModelRegistry, Node, Relationship
from ...core.graph import GraphDataModel


def _convert_enum_values(value: Any) -> Any:
    """Convert enum values to their underlying values for Neo4j storage."""
    if hasattr(value, 'value'):
        return value.value
    return value


def get_relationship_type_for_field(field_name: str, custom_type: Optional[str] = None) -> str:
    """
    Get the relationship type for a complex property field.
    
    Uses the .NET convention: "__PROPERTY__{fieldName}__"
    """
    if custom_type:
        return custom_type
    return GraphDataModel.property_name_to_relationship_type_name(field_name)


class Neo4jSerializer:
    """Serialization utilities for Neo4j graph database operations."""

    @staticmethod
    def serialize_node(node: Node) -> SerializedNode:
        """
        Serialize a node to Neo4j format using the new type detection system.
        """
        node_type = type(node)
        metadata = getattr(node_type, '__graph_node_metadata__', None)
        if metadata:
            labels = [metadata['label']]
        else:
            labels = [node_type.__name__]
        from pydantic import BaseModel
        import json
        properties = {}
        complex_properties = {}
        for field_name, field_info in node.__class__.model_fields.items():
            value = getattr(node, field_name, None)
            if value is None:
                continue
            # Embedded Pydantic model
            if isinstance(value, BaseModel):
                properties[field_name] = json.dumps(value.model_dump())
            # List of embedded models
            elif isinstance(value, list) and value and isinstance(value[0], BaseModel):
                properties[field_name] = json.dumps([item.model_dump() for item in value])
            # Dict fields
            elif isinstance(value, dict):
                properties[field_name] = json.dumps(value)
            # Primitive
            else:
                properties[field_name] = value
        return SerializedNode(id=node.id, labels=labels, properties=properties, complex_properties=complex_properties)

    @staticmethod
    def serialize_relationship(relationship: Relationship) -> SerializedRelationship:
        """
        Serialize a relationship to Neo4j format.

        Args:
            relationship: The relationship to serialize.

        Returns:
            SerializedRelationship with properties.
        """
        # Get relationship metadata
        rel_type = type(relationship)
        metadata = getattr(rel_type, '__graph_relationship_metadata__', None)
        if metadata:
            type_name = metadata['label']
        else:
            type_name = rel_type.__name__

        # Use ModelRegistry to get field information
        properties = {}
        
        for field_name, field_info in rel_type.model_fields.items():
            value = getattr(relationship, field_name, None)
            if value is None:
                continue
                
            # Get processed field info from registry
            processed_info = ModelRegistry.get_field_info(rel_type, field_name)
            if not processed_info:
                continue
                
            # Relationships can only have simple properties
            if processed_info.storage_type == FieldStorageType.SIMPLE:
                properties[field_name] = _convert_enum_values(value)

        return SerializedRelationship(
            id=relationship.id,
            type=type_name,
            start_node_id=relationship.start_node_id,
            end_node_id=relationship.end_node_id,
            properties=properties,
            complex_properties={}  # Relationships cannot have complex properties
        )

    @staticmethod
    def deserialize_relationship(
        record: Record,
        relationship_type: Type[Relationship],
        complex_properties: Optional[Dict[str, Any]] = None
    ) -> Relationship:
        """
        Deserialize a Neo4j record to a relationship.
        """
        rel_data = dict(record.get('r', {}))
        # Handle Neo4j DateTime objects
        for key, value in rel_data.items():
            if hasattr(value, 'to_native'):
                rel_data[key] = value.to_native()
        # Convert JSON strings to dict for fields that expect dicts
        import json
        for field_name, field_info in getattr(relationship_type, 'model_fields', {}).items():
            expected_type = getattr(field_info, 'annotation', None)
            if expected_type is dict or (hasattr(expected_type, '__origin__') and expected_type.__origin__ is dict):
                val = rel_data.get(field_name)
                if isinstance(val, str):
                    try:
                        decoded = json.loads(val)
                        if isinstance(decoded, dict):
                            rel_data[field_name] = decoded
                    except Exception:
                        pass
        return relationship_type(**rel_data)

    @staticmethod
    def deserialize_node(
        record: Record,
        node_type: Type[Node],
        complex_properties: Optional[Dict[str, Any]] = None
    ) -> Node:
        """
        Deserialize a Neo4j record to a node.
        """
        node_data = dict(record.get('n', {}))
        # Handle Neo4j DateTime objects
        for key, value in node_data.items():
            if hasattr(value, 'to_native'):
                node_data[key] = value.to_native()
        import json
        from pydantic import BaseModel
        from typing import Union, get_args, get_origin
        for field_name, field_info in getattr(node_type, 'model_fields', {}).items():
            expected_type = getattr(field_info, 'annotation', None)
            val = node_data.get(field_name)
            # Dict fields
            if expected_type is dict or (hasattr(expected_type, '__origin__') and expected_type.__origin__ is dict):
                if isinstance(val, str):
                    try:
                        decoded = json.loads(val)
                        if isinstance(decoded, dict):
                            node_data[field_name] = decoded
                    except Exception:
                        pass
            # Handle Union types (like Optional[T])
            elif get_origin(expected_type) is Union:
                # Extract the actual types from the Union
                union_types = get_args(expected_type)
                # Find the first Pydantic model type in the Union
                model_type = None
                for union_type in union_types:
                    if isinstance(union_type, type) and issubclass(union_type, BaseModel):
                        model_type = union_type
                        break
                # If we found a model type, try to deserialize
                if model_type and isinstance(val, str):
                    try:
                        decoded = json.loads(val)
                        if isinstance(decoded, dict):
                            node_data[field_name] = model_type(**decoded)
                    except Exception:
                        pass
            # Any Pydantic model field (embedded or related)
            elif isinstance(expected_type, type) and issubclass(expected_type, BaseModel):
                if isinstance(val, str):
                    try:
                        decoded = json.loads(val)
                        if isinstance(decoded, dict):
                            node_data[field_name] = expected_type(**decoded)
                    except Exception:
                        pass
            # List of Pydantic models
            elif hasattr(expected_type, '__origin__') and expected_type.__origin__ is list:
                item_type = expected_type.__args__[0]
                if isinstance(item_type, type) and issubclass(item_type, BaseModel):
                    if isinstance(val, str):
                        try:
                            decoded = json.loads(val)
                            if isinstance(decoded, list):
                                node_data[field_name] = [item_type(**item) if isinstance(item, dict) else item for item in decoded]
                        except Exception:
                            pass
        return node_type(**node_data)

    @staticmethod
    def get_complex_property_cypher(
        parent_alias: str,
        field_name: str,
        relationship_type: str,
        target_alias: Optional[str] = None
    ) -> str:
        """
        Generate Cypher for loading complex properties.

        Uses the same pattern as .NET CypherQueryBuilder for complex property loading.

        Args:
            parent_alias: The alias of the parent node.
            field_name: The name of the complex property field.
            relationship_type: The relationship type to use.
            target_alias: The alias for the target node (optional).

        Returns:
            Cypher query fragment for loading complex properties.
        """
        if target_alias is None:
            target_alias = f"{field_name}_node"

        # Use the .NET pattern for complex property loading
        return f"""
        OPTIONAL MATCH ({parent_alias})-[{field_name}_rel:{relationship_type}]->({target_alias})
        WHERE type({field_name}_rel) STARTS WITH '{GraphDataModel.PROPERTY_RELATIONSHIP_TYPE_NAME_PREFIX}'
        """

    @staticmethod
    def get_complex_property_return(
        field_name: str,
        target_alias: Optional[str] = None
    ) -> str:
        """
        Generate Cypher return clause for complex properties.

        Args:
            field_name: The name of the complex property field.
            target_alias: The alias for the target node (optional).

        Returns:
            Cypher return clause fragment.
        """
        if target_alias is None:
            target_alias = f"{field_name}_node"

        return f"{field_name}: {target_alias}"
