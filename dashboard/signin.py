import streamlit as st
import os

from dashboard.funciones import apiPost


base_dir = os.getcwd() 
logo = os.path.join(base_dir, 'images', 'logo.png')

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

    

c1,c2 = st.columns([1, 3])
with c1:
    st.image(logo)
with c2:
    # st.subheader('Autorización')
    with st.form(key='my_form'):
        st.write("Por favor ingrese usuario y contraseña")
        
        st.text_input("Usuario", key="usuario", placeholder="Ingrese del usuario")
        st.text_input("Contraseña", key="clave", type="password", placeholder="Contraseña del usuario")
        submit = st.form_submit_button(label='Ingresar', on_click=func_login)
        
        
        