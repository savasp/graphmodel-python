# Integration Tests for Neo4j

This directory contains integration tests that run against a real Neo4j database instance. These tests use the actual `Neo4jGraph` and `Neo4jDriver` classes and verify end-to-end functionality, including node and relationship creation, querying, updating, and deletion.

## How to Run

To run only the integration tests:

```
pytest tests/integration/ -m integration
```

Or, to run all tests including integration:

```
pytest
```

## Requirements

- A running Neo4j instance (see the main project README for setup)
- The test database will be cleaned before/after each test

## Test Coverage

- Node CRUD operations
- Relationship CRUD operations
- Querying (filtering, ordering, pagination)
- Embedded and related fields
- Error handling
