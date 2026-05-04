import streamlit as st 
from api_activate import use_api

food_name = st.text_input('Recherchez le nom', value="cheese")

st.dataframe(use_api(food_name))