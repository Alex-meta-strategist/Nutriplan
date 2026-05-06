import logging
import pandas as pd
import streamlit as st
from functools import lru_cache
import requests
from io import BytesIO

logger = logging.getLogger(__name__)

# Correct direct link to CIQUAL 2025 Excel
CIQUAL_XLSX_URL = "https://entrepot.recherche.data.gouv.fr/api/access/datafile/:persistentId?persistentId=doi:10.57745/RPWYZD"

DEFAULT_NAME_COL = "alim_nom_fr"


@lru_cache(maxsize=1)
def load_ciqual_full() -> pd.DataFrame:
    """Download CIQUAL with SSL bypass for problematic networks"""
    try:
        logger.info("Downloading CIQUAL 2025 table (1.5 MB)...")
        
        # Bypass SSL verification
        resp = requests.get(CIQUAL_XLSX_URL, verify=False, timeout=90)
        resp.raise_for_status()
        
        df = pd.read_excel(BytesIO(resp.content), engine="openpyxl", dtype=str)
        
        logger.info(f"✅ CIQUAL 2025 loaded successfully — {len(df):,} foods")
        return df
        
    except Exception as e:
        logger.error("CIQUAL download failed: %s", e)
        st.error("❌ Failed to download CIQUAL. Check your internet or network settings.")
        return pd.DataFrame()


def search_ciqual(food_name: str, max_results: int = 50) -> pd.DataFrame:
    needle = str(food_name or "").strip()
    if not needle:
        return pd.DataFrame()

    df = load_ciqual_full()
    if df.empty:
        return pd.DataFrame()

    # Find name column
    if DEFAULT_NAME_COL in df.columns:
        name_col = DEFAULT_NAME_COL
    else:
        candidates = [c for c in df.columns if any(k in str(c).lower() for k in ["nom", "lib", "aliment"])]
        name_col = candidates[0] if candidates else df.columns[0]

    mask = df[name_col].astype(str).str.contains(needle, case=False, na=False)
    return df[mask].head(max_results)