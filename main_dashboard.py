import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
import math 

st.set_page_config(
    page_title="🔥 Dashboard de Recomendación de Películas 🔥",
    page_icon="🎬",#https://docs.streamlit.io/develop/api-reference/navigation/st.page
    layout="wide"
)

if __name__ == "__main__":
    pages = []
    pages.append(st.Page("dashboard/acercade.py", title="Acerca de", icon=":material/sell:", default=True))
    pages.append(st.Page("dashboard/recomendacion.py", title="Recomendación de Películas", icon=":material/star_outline:"))
    pages.append(st.Page("dashboard/analisis.py", title="Análisis de Datos", icon=":material/area_chart:"))
    pg = st.navigation(pages, position="top")
 
pg.run()