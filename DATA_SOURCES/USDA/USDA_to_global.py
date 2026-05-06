import pandas as pd
from DATA_SOURCES.USDA.USDA_api_activate import use_usda_api


def USDA_to_global(food_name: str) -> pd.DataFrame:
    df = use_usda_api(food_name)
    if df.empty:
        return pd.DataFrame()
    food_info = df

    nutrient_rows = []
    for _, row in food_info.iterrows():
        nutrients = row.get("foodNutrients", [])
        nutrient_dict = {}

        if isinstance(nutrients, list):
            for nutrient in nutrients:
                if not isinstance(nutrient, dict):
                    continue
                nutrient_name = nutrient.get("nutrientName")
                value = nutrient.get("value")
                unit = nutrient.get("unitName")

                if nutrient_name is None or value is None:
                    continue

                col_name = f"{nutrient_name}" 
                nutrient_dict[col_name] = f"{value} {unit}" if unit else str(value)

        nutrient_rows.append(nutrient_dict)

    food_nutrients = pd.DataFrame(nutrient_rows)
    food_global = pd.concat([food_info.drop(columns="foodNutrients", errors="ignore"), food_nutrients], axis=1)
    return food_global