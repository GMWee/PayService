from decimal import Decimal
from urllib.parse import urlencode, quote

import aiohttp
import json
import time
import logging

from src.base.config import CONFIG

logger = logging.getLogger(__name__)

class PaymentLink:
    async def get_quickpay_link(self, sum: float, user_id: int):
        try:
            sum = float(sum)
        except (ValueError, IndexError):
            logger.error(f"Invalid callback data format in sub_buy: {sum}")
            return {"error": "Invalid data format"}

        try:
            expected_price = Decimal(sum)
        except (TypeError, IndexError):
            return {"error": f"Error for up payment for {sum}"}

        label = f"payment_{user_id}_{sum:.2f}_{int(time.time())}"
        payment_url = self.create_quickpay_link(
            amount=float(expected_price),
            label=label,
            targets=f"Пополнение {sum}"
        )
        logger.info(f"Generated payment link for user {user_id}, label {label}, price {expected_price}")
        return {
            "label": label,
            "url": payment_url
        }

    def create_quickpay_link(self, amount: float, label: str, targets: str, payment_type="AC"):
        params = {
            "receiver": CONFIG.yoomoney_receiver,
            "quickpay-form": "shop",
            "targets": targets,
            "paymentType": payment_type,
            "sum": amount,
            "label": label,
            "successURL": ""
        }
        encoded_params = urlencode({k: str(v) for k, v in params.items()}, quote_via=quote)
        quickpay_url = f"https://yoomoney.ru/quickpay/confirm.xml?{encoded_params}"
        return quickpay_url

    async def check_payment_handler(self, label: str, user_id: int):
        logger.info(f"Checking payment for user {user_id} with label: {label}")
        payment_successful = await self.check_yoomoney_payment(CONFIG.yoomoney_access_token, label)
        if payment_successful == 1:
            logger.info(f"Payment SUCCESSFUL for user {user_id}, label: {label}")
            return 1
        else:
            logger.warning(f"Payment FAILED or PENDING for user {user_id}, label: {label}")
            return 0

    async def check_yoomoney_payment(self, access_token: str, label: str, records: int = 10) -> bool:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "label": label,
            "records": records,
            "type": "deposition",
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(CONFIG.yoomoney_scopes, headers=headers, data=data) as response:
                    logger.debug(f"YooMoney API request: URL={CONFIG.yoomoney_scopes}, Headers={headers}, Data={data}")
                    logger.debug(f"YooMoney API response status: {response.status}")

                    if response.status == 200:
                        try:
                            result = await response.json()
                            logger.debug(f"YooMoney API response JSON: {result}")

                            if "operations" in result:
                                for operation in result["operations"]:
                                    if operation.get("label") == label and operation.get("status") == "success":
                                        logger.info(f"Payment found and successful for label: {label}")
                                        return 1
                                logger.warning(f"Payment with label '{label}' not found or not successful in recent operations.")
                                return 0
                            elif "error" in result:
                                logger.error(f"YooMoney API error: {result['error']}")
                                return 0
                            else:
                                logger.error(f"Unexpected YooMoney API response structure: {result}")
                                return 0
                        except json.JSONDecodeError:
                            logger.exception("Failed to decode YooMoney API response JSON.")
                            return 0
                        except Exception as e:
                            logger.exception(f"Error processing YooMoney API response: {e}")
                            return 0
                    else:
                        error_text = await response.text()
                        logger.error(f"YooMoney API request failed with status {response.status}: {error_text}")
                        return 0

            except aiohttp.ClientConnectorError as e:
                logger.exception(f"Could not connect to YooMoney API: {e}")
                return 0
            except Exception as e:
                logger.exception(f"An unexpected error occurred during YooMoney API call: {e}")
                return 0

PaymentLink = PaymentLink()