import streamlit as st 
from DATA_SOURCES.OFF.OFF_to_global import OFF_to_global
from DATA_SOURCES.USDA.USDA_to_global import USDA_to_global
from DATA_SOURCES.CIQUAL.ciqual import search_ciqual
from NORMALIZATION.normalize import normalize
import pandas as pd

food_name = st.text_input('Recherchez le nom', value="cheese")

col1, col2, col3 = st.columns(3)
with col1:
    db = st.multiselect("Database", ["usda", "Ciqual"], default=["usda"])
with col2:
    brand = st.text_input('Brand', value=None)
with col3:
    barcode = st.text_input('Barcode', value=None)

if st.button("search"):

    df = pd.DataFrame()
    if "usda" in db:
        usda_flat = USDA_to_global(food_name)
        if usda_flat.empty:
            st.info("usda: no result found for this search.")
        else:    
            df = pd.concat([df, normalize(usda_flat, 'usda')])  

    if barcode and str(barcode).strip():
        off_flat = OFF_to_global(str(barcode).strip())        
        if off_flat.empty:
            st.info("Open Food Facts: no product found for this barcode.")
        else:
            df = pd.concat([df, normalize(off_flat, 'off')]) 

    if "Ciqual" in db:
        ciqual_flat = search_ciqual(food_name)
        if ciqual_flat.empty:
            st.info("CIQUAL: no result found for this search.")
        else:
            df = pd.concat([df, normalize(ciqual_flat, 'ciqual')]) 

    st.dataframe(df)