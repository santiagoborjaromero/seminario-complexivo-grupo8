import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(
    page_title="🔥 Recomendacion de Películas 🔥",
    page_icon="🔥", #https://docs.streamlit.io/develop/api-reference/navigation/st.page
    layout="wide"
)

st.title(" 🔥 Dashboard Recomendacíon Hibrida de Películas 🔥 ")