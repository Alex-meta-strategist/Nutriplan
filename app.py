import streamlit as st

# Define the pages
page_1 = st.Page("pages/page_1.py", title="search", icon="🎈")


# Set up navigation
pg = st.navigation([page_1])

# Run the selected page
pg.run()