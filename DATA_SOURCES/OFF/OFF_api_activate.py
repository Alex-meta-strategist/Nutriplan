import logging
import httpx
import pandas as pd

logger = logging.getLogger(__name__)

def call_api_endpoint(url: str) -> httpx.Response:
    headers = {"User-Agent": "Nutriplan/1.0 (https://world.openfoodfacts.org)"}
    try:
        with httpx.Client(headers=headers) as client:
            logger.debug("url: %s", url)
            response = client.get(url)
            if response.status_code == 404:
                return response
            response.raise_for_status()
            try:
                parsed = response.json()
                logger.debug(
                    "Response JSON keys: %s",
                    list(parsed.keys()) if isinstance(parsed, dict) else type(parsed),
                )
            except ValueError:
                logger.debug("Non-JSON body preview: %s", response.text[:200])
            return response
    except Exception as e:
        logger.error("Unexpected error occurred: %s", e)
        return httpx.Response(status_code=500, content=b"Unexpected error")


def use_off_api(barcode: str) -> pd.DataFrame:
    
    try:
        api_response = call_api_endpoint(
            "https://world.openfoodfacts.org/api/v2/product/"
            f"{barcode}?fields=product_name,nutriments"
        )
        if api_response.status_code in (200, 404):
            try:
                payload = api_response.json()
            except ValueError:
                logger.error("OFF response was not JSON (status %s)", api_response.status_code)
                return pd.DataFrame()
            if payload.get("status") != 1:
                return pd.DataFrame()
            product = payload.get("product")
            if not isinstance(product, dict):
                return pd.DataFrame()
            return pd.DataFrame([product])
        logger.error("API returned status code: %s", api_response.status_code)
        return pd.DataFrame()
    except Exception as e:
        logger.error("Error in use_off_api: %s", e)
        return pd.DataFrame()
