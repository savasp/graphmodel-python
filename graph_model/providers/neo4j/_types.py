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
Type stubs for Neo4j async driver when proper types are not available.
"""

from typing import Protocol, Any, Optional, Dict, runtime_checkable


@runtime_checkable
class AsyncResult(Protocol):
    """Protocol for Neo4j async result."""
    async def single(self) -> Optional[Any]: ...
    async def to_list(self) -> list[Any]: ...


@runtime_checkable  
class AsyncSession(Protocol):
    """Protocol for Neo4j async session."""
    async def run(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> AsyncResult: ...
    async def close(self) -> None: ...
    async def __aenter__(self) -> "AsyncSession": ...
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...


@runtime_checkable
class AsyncDriver(Protocol):
    """Protocol for Neo4j async driver."""
    def session(self, **kwargs: Any) -> AsyncSession: ...
    async def close(self) -> None: ...


@runtime_checkable
class AsyncGraphDatabase(Protocol):
    """Protocol for Neo4j async graph database."""
    @staticmethod
    def driver(uri: str, *, auth: Optional[tuple[str, str]] = None, **kwargs: Any) -> AsyncDriver: ...
