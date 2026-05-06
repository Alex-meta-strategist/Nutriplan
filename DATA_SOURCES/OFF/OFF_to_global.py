import pandas as pd
import json
import logging
from typing import Any
from DATA_SOURCES.OFF.OFF_api_activate import use_off_api

logger = logging.getLogger(__name__)


def parse_nutriments_json(nutriments: Any) -> dict:
    """Safely parse nutriments."""
    if not nutriments or pd.isna(nutriments):
        return {}
    try:
        return nutriments if isinstance(nutriments, dict) else json.loads(nutriments)
    except Exception:
        logger.warning("Failed to parse nutriments")
        return {}


def OFF_to_global(food_name: str) -> pd.DataFrame:
    """Search Open Food Facts → return product_name + all nutrients per 100g."""
    try:
                
        df = use_off_api(food_name)
        if df.empty:
            return pd.DataFrame()

        # Build list of flattened rows
        rows = []
        for _, row in df.iterrows():
            nutriments = parse_nutriments_json(row.get("nutriments"))
            
            flat = {"product_name": row.get("product_name", "")}
            flat.update({k: v for k, v in nutriments.items() if not k.endswith("_unit")})
            rows.append(flat)

        if not rows:
            return pd.DataFrame()

        result = pd.DataFrame(rows)
        
        # Put product_name first
        cols = ["product_name"] + [c for c in result.columns if c != "product_name"]
        result = result[cols]

        result = result.rename(columns={"product_name": "Product Name"})

        return result

    except Exception as e:
        logger.error("Error in OFF_to_global for '%s': %s", food_name, e)
        return pd.DataFrame()