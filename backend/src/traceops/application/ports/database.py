"""Database ports defining interfaces required by application use cases."""

from typing import Protocol


class DatabaseHealthPort(Protocol):
    """Port for verifying database operational readiness."""

    async def check_health(self) -> bool:
        """Check if the database is accessible and accepting queries.

        Returns:
            bool: True if database responded successfully, False otherwise.
        """
        ...
