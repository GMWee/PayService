import asyncio
import asyncpg

class Database:
	def __init__(self):
		self.connection: asyncpg.Connection = None  # Initialize to None
		self._last_row_id: int = 0

	async def open_connection(self, path: str) -> None:
		self.connection = await asyncpg.connect(path)  # Remove autocommit=True

	async def close_connection(self) -> None:
		if self.connection:
			await self.connection.close()

	async def execute_query(self, query: str, params: tuple = None) -> None:
		async with self.connection.transaction():  # Start a transaction
			await self.connection.execute(query, *(params or ()))  # Use execute directly

	# asyncpg does not directly expose lastrowid.  This will need to be handled separately
	# if it is needed in a specific query.  Consider using RETURNING id in INSERT/UPDATE.

	async def execute_get_query(self, query: str, params: tuple = None):
		return await self.connection.fetch(query, *(params or ()))  # Use fetch directly

	@property
	def last_id(self):
		return self._last_row_id  # This property likely doesn't work correctly with asyncpg.  See comment above.


class ProjectDatabase(Database):
	def __init__(self):
		super().__init__()

		async def get_or_create_key(self, id: int, create_if_not_found: bool = True):
			res = await self.execute_get_query("SELECT * FROM api_key WHERE id = $1", (id,))
			if not res and create_if_not_found:
				await self.execute_query("INSERT INTO api_key(id) VALUES ($1)", (id,))
				res = await self.execute_get_query("SELECT * FROM api_key WHERE id = $1", (id,))
				return res[0] if res else None  # Corrected handling of empty result.
			return res[0] if res else None

		async def set_key(self, user_id: int, key: str, value: int | str | float):
			await self.execute_query(f"UPDATE api_key SET {key} = $1 WHERE id = $2", (value, user_id))

DATABASE = ProjectDatabase()