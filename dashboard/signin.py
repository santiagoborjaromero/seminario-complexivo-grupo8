import streamlit as st
import json

from dashboard.funciones import apiPost

st.set_page_config(
    page_title="🔥 Mis Películas 🔥",
    page_icon="🎬",#https://docs.streamlit.io/develop/api-reference/navigation/st.page
    layout="centered"
)

st.subheader('Autorización')

def func_login():
    # st.write(st.session_state)
    params = {
        "usuario": st.session_state["usuario"],
        "clave": st.session_state["clave"]
    }
    resp = apiPost("/login", data=params)
    if resp["status"]:
        data = resp["data"]
        if data == {}:
            st.session_state.user_data = {}
            st.session_state.logged_in = False    
            st.error(resp.get("message", ""))
        else:
            st.session_state.user_data = data
            st.session_state.logged_in = True
    else:
        st.session_state.user_data = {}
        st.session_state.logged_in = False
        st.error(resp.get("message", ""))

    

with st.form(key='my_form'):
    st.write("Por favor ingrese usuario y contraseña")
    
    st.text_input("Usuario", key="usuario", placeholder="Ingrese del usuario")
    st.text_input("Contraseña", key="clave", type="password", placeholder="Contraseña del usuario")
    submit = st.form_submit_button(label='Ingresar', on_click=func_login)
    
        
    