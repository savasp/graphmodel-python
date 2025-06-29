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
Async Neo4j driver and session management for the Python Graph Model library.
"""

from typing import Any, Optional, Tuple, Dict

try:
    from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession  # type: ignore
except ImportError:
    AsyncDriver = Any  # type: ignore
    AsyncGraphDatabase = Any  # type: ignore
    AsyncSession = Any  # type: ignore


class Neo4jDriver:
    """
    Singleton-style async Neo4j driver and connection pool.
    """
    _driver: Optional[Any] = None
    _uri: Optional[str] = None
    _auth: Optional[Tuple[str, str]] = None
    _database: Optional[str] = None

    @classmethod
    async def initialize(
        cls, 
        uri: str, 
        user: str, 
        password: str, 
        database: Optional[str] = None, 
        **kwargs: Any
    ) -> None:
        if cls._driver is not None:
            await cls.close()
        cls._uri = uri
        cls._auth = (user, password)
        cls._database = database
        cls._driver = AsyncGraphDatabase.driver(uri, auth=(user, password), **kwargs)  # type: ignore

    @classmethod
    def get_database(cls) -> Optional[str]:
        return cls._database

    @classmethod
    async def ensure_database_exists(cls) -> None:
        if cls._database is None:
            raise ValueError("Database is not set. Call Neo4jDriver.initialize() with a database name first.")
        driver = cls.get_driver()
        async with driver.session() as session:  # type: ignore
            await session.run(f"CREATE DATABASE {cls._database} IF NOT EXISTS WAIT 10 SECONDS")  # type: ignore

    @classmethod
    def get_driver(cls) -> Any:
        if cls._driver is None:
            raise RuntimeError("Neo4j driver not initialized. Call Neo4jDriver.initialize() first.")
        return cls._driver

    @classmethod
    async def close(cls) -> None:
        if cls._driver is not None:
            await cls._driver.close()  # type: ignore
            cls._driver = None

    @classmethod
    def session(cls, **kwargs: Any) -> Any:
        """Get a new async session."""
        session_kwargs: Dict[str, Any] = kwargs.copy()
        if cls._database is not None and 'database' not in session_kwargs:
            session_kwargs['database'] = cls._database
        return cls.get_driver().session(**session_kwargs)  # type: ignore