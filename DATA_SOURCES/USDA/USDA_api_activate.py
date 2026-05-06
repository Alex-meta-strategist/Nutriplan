import pandas as pd 
import logging
import httpx
import streamlit as st

logger = logging.getLogger(__name__)

def call_api_endpoint(url: str) -> httpx.Response:

    try:
        with httpx.Client() as client:
            logger.debug(f"url: {url}")
            response = client.get(url)
            response.raise_for_status()
            logger.debug(f"Response JSON: {response.json()}")
            return response
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")
        return httpx.Response(status_code=500, content=b"Unexpected error")

def use_usda_api(food_name: str) -> pd.DataFrame:

    try:
        api_response = call_api_endpoint(
            f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={st.secrets['MY_API_KEY']}&query={food_name}"
        )
        if api_response.status_code == 200:
            food_data = api_response.json()
            foods = food_data.get("foods", [])
            return pd.DataFrame(foods)
        logger.error(f"API returned status code: {api_response.status_code}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error in use_api: {str(e)}")
        return pd.DataFrame()
