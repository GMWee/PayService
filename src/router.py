from fastapi import APIRouter
from src.base import PaymentLink
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get('/get_quickpay_link/{sum}/{user_id}')
async def get_quickpay_link(sum: float, user_id: int):
    data = await PaymentLink.get_quickpay_link(sum, user_id)
    return data

@router.get("/check_payment_handler/{label}/{user_id}")
async def check_payment_handler(label: str, user_id: int):
    data = await PaymentLink.check_payment_handler(label, user_id)
    print(data)
    return {
        'label': data
    }
