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

"""Exception classes for the graph model."""

from typing import Any, Optional


class GraphException(Exception):
    """
    Base exception for all graph-related errors.
    
    This exception is raised when any graph operation fails, including
    database connectivity issues, query errors, and data consistency problems.
    """

    def __init__(
        self, 
        message: str, 
        cause: Optional[Exception] = None,
        details: Optional[dict[str, Any]] = None
    ) -> None:
        super().__init__(message)
        self.cause = cause
        self.details = details or {}


class GraphValidationException(GraphException):
    """
    Exception raised when graph entity validation fails.
    
    This includes schema validation, constraint violations, and
    data type mismatches.
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Any = None,
        entity_type: Optional[type] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, cause)
        self.field_name = field_name
        self.field_value = field_value
        self.entity_type = entity_type


class GraphTransactionException(GraphException):
    """Exception raised when transaction operations fail."""

    pass


class GraphConnectionException(GraphException):
    """Exception raised when database connection operations fail."""

    pass


class GraphQueryException(GraphException):
    """Exception raised when query operations fail."""

    def __init__(
        self,
        message: str,
        query: Optional[str] = None,
        parameters: Optional[dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ) -> None:
        super().__init__(message, cause)
        self.query = query
        self.parameters = parameters or {} 