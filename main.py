from fastapi import FastAPI
from src.router.router import router
import logging
from src.base.config import CONFIG
from src.base.database import DATABASE

app = FastAPI()
app.include_router(router)


@app.on_event("startup")
async def startup_event():
	# Загрузка конфига если нужно
	CONFIG.load_config("run/config.json")
	
	# Открытие соединения с БД
	await DATABASE.open_connection(
		CONFIG["database_host"],
		CONFIG["database_port"],
		CONFIG["database_user"],
		CONFIG["database_password"],
		CONFIG["database_database"],
	)
	logging.info("Database connection opened")


@app.on_event("shutdown")
async def shutdown_event():
	await DATABASE.close_connection()
	logging.info("Database connection closed")


# Этот блок выполняется только при прямом запуске файла
if __name__ == "__main__":
	import uvicorn
	
	uvicorn.run(app, host="0.0.0.0", port=8000)