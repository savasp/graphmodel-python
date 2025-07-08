# Plan: Evolving Python Graph Model to Annotation-Only Field Definitions

## 1. Overview

Based on the .NET implementation and requirements, this plan outlines the evolution of the Python `graph_model` package to support simplified annotation-only field definitions while maintaining compatibility with the .NET approach.

## 2. Key Design Principles

### 2.1 Field Type Detection Rules (Following .NET Logic)

```python
# Simple Types (stored as direct properties)
- Primitive types: str, int, float, bool, bytes
- Date/time: datetime, date, time
- Other: UUID, Decimal
- Enums
- Collections of simple types: List[str], List[int], List[Enum], Dictionaries[string, <simple type>], etc.
- Anything that can be natively supported by the Neo4j primitive data type system.

# Complex Types (types that are not considered simple)
- Any class that doesn't inherit from Node/INode or Relationship/IRelationship
- Collections of complex types: List[Address], etc.
- Pydantic models that aren't Nodes or Relationships
- Properties of these types are stored as separate Neo4j graph nodes using "private" relationships. Such relationships cannot be discovered via the query interfaces nor traversed explicitly. These private relationships are only used to re-materialize nodes when they are included in the Cypher RETURN (e.g. returning nodes, returning path segments, or projections that include nodes).
- See /Users/savasp/dev/brainexpanded/services/graphmodel/dotnet/src/Graph.Model/Utils/GraphDataModel.cs for what is considered a simple property (IsSimple). Everything else is considered complex unless the type implements INode or IRelationship, in which case it's not allowed. The GraphDataModel.PropertyNameToRelationshipTypeName() also shows how to create the neo4j relationship type for complex properties.

# Nodes
- Classes that inherit from Node
- Can have properties of simple types or collections of them
- Can have complex properties or collections of them

# Relationships
- Classes that inherit from Relationship
- Can have properties of simple types or collections of them.
- Relationships cannot have complex properties
```

We are not going to support properties of types that inherit from Node at this stage (what used to be called "related nodes").

### 2.2 Annotation-Based Configuration

```python
from typing import Annotated
from graph_model import Node, node, Indexed, Required, Default

@node("User")
class User(Node):
    # Simple property with indexing
    name: Annotated[str, Indexed] = "John"

    # Simple property with default
    age: Annotated[int, Default(25)] = 25

    # Required complex property
    home: Annotated[Address, Required] = None

    # Optional complex property
    work: Annotated[Address, Default(None)] = None

    # Collection of simple types
    tags: List[str] = []

    # Collection of complex types
    addresses: List[Address] = []
```

## 3. Implementation Plan

### Phase 1: Core Type Detection System

#### 3.1 Create New Type Detection Module

```python
# graph_model/core/type_detection.py
class TypeDetector:
    @staticmethod
    def is_simple_type(type_hint: Type) -> bool:
        """Follow .NET GraphDataModel.IsSimple() logic"""

    @staticmethod
    def is_complex_type(type_hint: Type) -> bool:
        """Follow .NET GraphDataModel.IsComplex() logic"""

    @staticmethod
    def is_related_type(type_hint: Type) -> bool:
        """Check if type inherits from Node"""
```

#### 3.2 Create Annotation-Based Configuration System

```python
# graph_model/attributes/annotations.py
from typing import Annotated, TypeVar, Any

T = TypeVar('T')

class Indexed:
    """Mark a field for indexing"""
    pass

class Required:
    """Mark a field as required"""
    pass

class Default(Generic[T]):
    """Provide a default value"""
    def __init__(self, value: T):
        self.value = value
```

### Phase 2: Model Registration and Processing

#### 3.3 Enhanced Model Registration

```python
# graph_model/core/model_registry.py
class ModelRegistry:
    def register_node_class(self, cls: Type[Node]) -> None:
        """Register a node class and process its fields"""
        # 1. Extract type annotations
        # 2. Detect field storage types
        # 3. Process annotations for configuration
        # 4. Store metadata for serialization/deserialization

    def get_field_info(self, cls: Type[Node], field_name: str) -> FieldInfo:
        """Get processed field information"""
```

#### 3.4 Field Processing Logic

```python
def process_field_annotations(cls: Type[Node], field_name: str, annotation: Any) -> FieldInfo:
    """Process field annotations to determine behavior"""

    # Handle Annotated types
    if get_origin(annotation) is Annotated:
        base_type, *metadata = get_args(annotation)

        # Extract configuration from metadata
        config = extract_config_from_metadata(metadata)

        # Determine storage type
        storage_type = TypeDetector.get_field_storage_type(base_type)

        return FieldInfo(
            storage_type=storage_type,
            indexed=Indexed in metadata,
            required=Required in metadata,
            default=extract_default(metadata),
            # ... other config
        )
    else:
        # Simple annotation - auto-detect
        storage_type = TypeDetector.get_field_storage_type(annotation)
        return FieldInfo(storage_type=storage_type)
```

### Phase 3: Serialization/Deserialization Updates

#### 3.5 Enhanced Serialization

```python
# graph_model/providers/neo4j/serialization.py
class Neo4jSerializer:
    def serialize_node(self, node: Node) -> SerializedNode:
        """Serialize node using new field detection"""
        cls = type(node)
        simple_props = {}
        complex_props = {}

        for field_name, field_info in cls.model_fields.items():
            value = getattr(node, field_name, None)
            if value is None:
                continue

            # Get processed field info from registry
            processed_info = ModelRegistry.get_field_info(cls, field_name)

            if processed_info.storage_type == FieldStorageType.SIMPLE:
                simple_props[field_name] = value
            elif processed_info.storage_type == FieldStorageType.RELATED:
                # Store for relationship creation
                complex_props[field_name] = {
                    'value': value,
                    'relationship_type': GraphDataModel.property_name_to_relationship_type_name(field_name)
                }
```

### Phase 4: Backward Compatibility Layer

We do not need to support backwards compatibility

## 4. New API Examples

### 4.1 Simple Usage (Desired Style)

```python
from graph_model import Node, node
from typing import Annotated, List

class Address:
    street: str
    city: str
    state: str

@node("User")
class User(Node):
    name: str = "John"
    email: Annotated[str, Indexed] = "john@example.com"
    age: Annotated[int, Default(25)] = 25
    home: Address = None  # Auto-detected as complex
    work: Optional[Address] = None # Auto-detected as a complex collection (use a "SequenceNumber" property on the private relationship to connect to the neo4j node that represents the complex property to capture order)
    tags: List[str] = []  # Auto-detected as simple collection
```

### 4.2 Advanced Configuration

```python
@node("Person")
class Person(Node):
    # Simple properties with configuration
    name: Annotated[str, Indexed, Required] = ""
    age: Annotated[int, Default(0)] = 0

    # Complex properties
    home_address: Annotated[Address] = None

    # Collections
    skills: List[str] = []  # Simple collection
    addresses: List[Address] = []  # Complex collection (embedded)
    friends: List[Person] = []  # Related collection
```

### 4.3 Relationship Definition

```python
@relationship("KNOWS")
class Knows(Relationship):
    since: datetime = None
    strength: Annotated[float, Default(1.0)] = 1.0

# Usage
person1 = Person(id="1", name="Alice")
person2 = Person(id="2", name="Bob")
knows = Knows(start_node_id="1", end_node_id="2", since=datetime.now())
```

## 5. Migration Strategy

### 5.1 Phase 1: Add New System Alongside Old

- Implement new type detection and annotation system
- No need to support the old system.

### 5.2 Phase 2: Update Examples and Tests

- Create new examples using annotation-only style
- Update tests to use new API
- No need to keep any tests for backwards compatibility.
- Re-organize the tests
- Remove any tests that aren't necessary anymore

### 5.3 Phase 3: Documentation and Migration Guide

- Update documentation to showcase new style
- No need to provide a migration guide
- Remove all outdated documentation

## 6. Testing Strategy

### 6.1 Unit Tests

```python
def test_type_detection():
    assert TypeDetector.is_simple_type(str) == True
    assert TypeDetector.is_simple_type(int) == True
    assert TypeDetector.is_complex_type(Address) == True
    assert TypeDetector.is_related_type(Person) == True

def test_annotation_processing():
    field_info = process_field_annotations(User, "name", Annotated[str, Indexed])
    assert field_info.storage_type == FieldStorageType.SIMPLE
    assert field_info.indexed == True
```

### 6.2 Integration Tests

```python
async def test_annotation_based_serialization():
    user = User(name="John", home=Address(street="123 Main"))
    serialized = await graph.create_node(user)
    # Verify simple field is stored directly
```

## 7. Implementation Order

1. **Week 1**: Core type detection system
2. **Week 2**: Annotation processing and model registry
3. **Week 3**: Serialization/deserialization updates
4. **Week 4**: Backward compatibility and testing
5. **Week 5**: Documentation and examples

## 8. Questions for Feedback

1. **Annotation Style**: Do you prefer the `Annotated[T, Config]` style or would you like a different approach?

Yes, let's go with the Annotated style. I have updated the plan above with my preferences.

2. **Configuration Options**: What configuration options are most important? (indexing, defaults, required, storage type overrides)

No storage type overrides but yes to the other.

3. **Relationship Handling**: Should relationships between nodes be defined in the node classes or always separate?

Always separate.

4. **Migration Timeline**: How quickly do you want to transition to the new API?

Implement all changes without worrying about migration. The package hasn't been released to anyone so we don't have to worry about backwards compatibility. We don't have to support any existing users.

5. **Field Detection Rules**: Are the proposed rules for simple vs complex vs related types correct?

I have updated the plan above with details.

6. **Backward Compatibility**: How important is maintaining compatibility with existing code?

Not at all. Ignore backwards compatibility altogether.

## 9. Alternative Approaches to Consider

From the options below, let's implement 9.3... hybrid.

### 9.1 Decorator-Based Configuration

```python
@node("User")
class User(Node):
    @indexed
    name: str = "John"

    @default(25)
    age: int = 25

    @embedded
    home: Address = None
```

### 9.2 Class-Level Configuration

```python
@node("User",
      indexed_fields=["name", "email"],
      embedded_fields=["home", "work"])
class User(Node):
    name: str = "John"
    email: str = "john@example.com"
    home: Address = None
    work: Address = None
```

### 9.3 Hybrid Approach

```python
@node("User")
class User(Node):
    # Auto-detected fields
    name: str = "John"
    home: Address = None

    # Explicitly configured fields
    email: Annotated[str, Indexed] = "john@example.com"
    age: Annotated[int, Default(25)] = 25
```

## 10. Implementation Details

I am leaving the implementation details to you.

## 11. Open Questions

1. **Performance**: How should we handle the performance impact of runtime type detection?

Caching

2. **Caching**: Should we cache field information to avoid repeated processing?

yes

3. **Error Handling**: How should we handle invalid annotations or conflicting configurations?

throw an exception

4. **Validation**: Should we validate field configurations at class definition time or runtime?

class definition.

5. **Documentation**: How should we document the new annotation system for users?

through the docs.
