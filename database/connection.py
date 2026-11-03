import os
import psycopg2
from psycopg2 import extensions
from psycopg2.extras import RealDictCursor


class CompatibleConnection(extensions.connection):

    def cursor(self, name=None, cursor_factory=None, **kwargs):
        dictionary = kwargs.pop("dictionary", False)

        if dictionary and cursor_factory is None:
            cursor_factory = RealDictCursor

        return super().cursor(
            name=name,
            cursor_factory=cursor_factory,
            **kwargs
        )

    def is_connected(self):
        return self.closed == 0


def DatabaseConnction():
    try:
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise RuntimeError("DATABASE_URL is missing from .env")

        connection = psycopg2.connect(
            database_url,
            sslmode=os.getenv("DB_SSLMODE", "require"),
            connection_factory=CompatibleConnection
        )

        return connection

    except psycopg2.Error as error:
        raise RuntimeError(
            f"Supabase PostgreSQL connection failed: {error}"
        ) from error