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
Async transaction context manager for Neo4j, implementing IGraphTransaction.
"""

from typing import Optional

from neo4j import AsyncSession, AsyncTransaction

from graph_model.core.transaction import IGraphTransaction


class Neo4jTransaction(IGraphTransaction):
    def __init__(self, session: AsyncSession):
        self._session = session
        self._tx: Optional[AsyncTransaction] = None
        self._is_committed = False
        self._is_rolled_back = False

    @property
    def is_active(self) -> bool:
        """Check if the transaction is currently active."""
        return self._tx is not None and not self._is_committed and not self._is_rolled_back

    @property
    def is_committed(self) -> bool:
        """Check if the transaction has been committed."""
        return self._is_committed

    @property
    def is_rolled_back(self) -> bool:
        """Check if the transaction has been rolled back."""
        return self._is_rolled_back

    async def commit(self) -> None:
        """Commit the transaction, making all changes permanent."""
        if self._tx is not None and not self._is_committed and not self._is_rolled_back:
            await self._tx.commit()
            self._is_committed = True

    async def rollback(self) -> None:
        """Roll back the transaction, discarding all changes."""
        if self._tx is not None and not self._is_committed and not self._is_rolled_back:
            await self._tx.rollback()
            self._is_rolled_back = True

    async def close(self) -> None:
        """Close the transaction, automatically rolling back if not committed."""
        if self._tx is not None and not self._is_committed and not self._is_rolled_back:
            await self.rollback()
        await self._session.close()

    async def __aenter__(self):
        self._tx = await self._session.begin_transaction()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
        await self._session.close()

    @property
    def transaction(self) -> AsyncTransaction:
        if self._tx is None:
            raise RuntimeError("Transaction not started.")
        return self._tx
