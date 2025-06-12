from fastapi import FastAPI
from src.router.router import router
import asyncio
import logging

from src.base.config import CONFIG
from src.base.database import DATABASE



class run:
	def __init__(self):
		pass
	
	async def run(self):
		await DATABASE.open_connection(
			CONFIG["database_host"],
			CONFIG["database_port"],
			CONFIG["database_user"],
			CONFIG["database_password"],
			CONFIG["database_database"],
		)
		
	