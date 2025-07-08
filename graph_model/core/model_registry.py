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
Model registry for processing field annotations and storing metadata.

This module provides utilities for registering node and relationship classes
and processing their field annotations to determine storage behavior.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Type, get_args, get_origin

from ..attributes.annotations import Default, Indexed, Required
from ..core.node import Node
from ..core.relationship import Relationship
from .type_detection import FieldStorageType, TypeDetector


@dataclass
class FieldInfo:
    """Metadata about a field in a graph entity."""
    
    storage_type: FieldStorageType
    indexed: bool = False
    required: bool = True
    default: Any = None
    default_factory: Optional[Any] = None


class ModelRegistry:
    """Registry for processing and storing field metadata for graph models."""
    
    _field_info_cache: Dict[Type, Dict[str, FieldInfo]] = {}
    
    @classmethod
    def register_node_class(cls, node_class: Type[Node]) -> None:
        """Register a node class and process its fields."""
        if node_class not in cls._field_info_cache:
            cls._field_info_cache[node_class] = {}
            
        # Process each field
        for field_name, field_info in node_class.model_fields.items():
            annotation = field_info.annotation
            processed_info = cls._process_field_annotations(field_name, annotation, field_info)
            cls._field_info_cache[node_class][field_name] = processed_info
    
    @classmethod
    def register_relationship_class(cls, relationship_class: Type[Relationship]) -> None:
        """Register a relationship class and process its fields."""
        if relationship_class not in cls._field_info_cache:
            cls._field_info_cache[relationship_class] = {}
            
        # Process each field
        for field_name, field_info in relationship_class.model_fields.items():
            annotation = field_info.annotation
            processed_info = cls._process_field_annotations(field_name, annotation, field_info)
            cls._field_info_cache[relationship_class][field_name] = processed_info
    
    @classmethod
    def get_field_info(cls, entity_class: Type, field_name: str) -> Optional[FieldInfo]:
        """Get processed field information for a field."""
        if entity_class not in cls._field_info_cache:
            # Auto-register if not already registered
            if issubclass(entity_class, Node):
                cls.register_node_class(entity_class)
            elif issubclass(entity_class, Relationship):
                cls.register_relationship_class(entity_class)
            else:
                return None
                
        return cls._field_info_cache.get(entity_class, {}).get(field_name)
    
    @classmethod
    def _process_field_annotations(cls, field_name: str, annotation: Any, field_info: Any) -> FieldInfo:
        """Process field annotations to determine behavior."""
        
        # Handle Annotated types
        if get_origin(annotation) is not None and get_origin(annotation).__name__ == 'Annotated':
            base_type, *metadata = get_args(annotation)
            
            # Extract configuration from metadata
            config = cls._extract_config_from_metadata(metadata)
            
            # Determine storage type
            storage_type = TypeDetector.get_field_storage_type(base_type)
            
            return FieldInfo(
                storage_type=storage_type,
                indexed=config.get('indexed', False),
                required=config.get('required', True),
                default=config.get('default', field_info.default if hasattr(field_info, 'default') else None),
                default_factory=config.get('default_factory', field_info.default_factory if hasattr(field_info, 'default_factory') else None)
            )
        else:
            # Simple annotation - auto-detect
            storage_type = TypeDetector.get_field_storage_type(annotation)
            return FieldInfo(
                storage_type=storage_type,
                indexed=False,
                required=True,
                default=field_info.default if hasattr(field_info, 'default') else None,
                default_factory=field_info.default_factory if hasattr(field_info, 'default_factory') else None
            )
    
    @classmethod
    def _extract_config_from_metadata(cls, metadata: List[Any]) -> Dict[str, Any]:
        """Extract configuration from annotation metadata."""
        config = {
            'indexed': False,
            'required': True,
            'default': None,
            'default_factory': None
        }
        
        for item in metadata:
            if isinstance(item, Indexed):
                config['indexed'] = True
            elif isinstance(item, Required):
                config['required'] = True
            elif isinstance(item, Default):
                config['default'] = item.value
        
        return config 