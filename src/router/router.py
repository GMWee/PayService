from fastapi import APIRouter
from src.router.paylink import PaymentLink
import logging

from src.base.database import DATABASE

logger = logging.getLogger(__name__)
router = APIRouter()



@router.get('/get_quickpay_link/{sum}/{user_id}/{key}/{service_name}')
async def get_quickpay_link(sum: float, user_id: int, key: str, service_name: str):
	if await logger_key_info(service_name, key) == 1:
		data = await PaymentLink.get_quickpay_link(sum, user_id)
		return data
	else:
		{"error": "api key error"}

@router.get("/check_payment_handler/{label}/{user_id}/{key}/{service_name}")
async def check_payment_handler(label: str, user_id: int, key: str, service_name: str):
	if await logger_key_info(service_name, key) == 1:
		return {'label': await PaymentLink.check_payment_handler(label, user_id)}
	else:
		return {"error": "api key error"}
async def logger_key_info(service_name, key):
	print(await DATABASE.get_key(service_name, key) )
	return 1 if await DATABASE.get_key(service_name, key) == 1 else 0