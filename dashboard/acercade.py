import streamlit as st
import os

BASE_DIR = os.getcwd() 
print(BASE_DIR)
M = os.path.join(BASE_DIR, 'images', 'M.png')
F = os.path.join(BASE_DIR, 'images', 'F.png')

current_user = st.session_state.user_data

if "logged_in" not in st.session_state or current_user == {}:
    st.session_state.logged_in = False
    st.session_state.user_data = {}

if (current_user["genero"] == "M"):
    st.sidebar.image(M,f"{current_user["nombre"]}")
else:
    st.sidebar.image(F,f"{current_user["nombre"]}")

st.sidebar.caption(f"Rating Votado {current_user["rating"]:.1f} ⭐ ({current_user["votos"]:,} votos)")
st.sidebar.caption(f":material/mail: {current_user["email"]}")
st.sidebar.caption(f":material/explore_nearby: {current_user["provincia"]}")
    
st.image("images/portada.png", width="stretch")
