import streamlit as st
import os

# st.set_page_config(
#     page_title="Ex-stream-ly Cool App",
#     page_icon="🧊",
#     layout="wide",
#     initial_sidebar_state="expanded",
#     menu_items={
#         'Get Help': 'https://www.extremelycoolapp.com/help',
#         'Report a bug': "https://www.extremelycoolapp.com/bug",
#         'About': "# This is a header. This is an *extremely* cool app!"
#     }
# )


base_dir = os.getcwd() 
M = os.path.join(base_dir, 'images', 'M.png')
F = os.path.join(base_dir, 'images', 'F.png')
logo = os.path.join(base_dir, 'images', 'logo.png')

current_user = st.session_state.user_data

if "logged_in" not in st.session_state or current_user == {}:
    st.session_state.logged_in = False
    st.session_state.user_data = {}

c1,c2 = st.columns(2)
with c1:
    with st.container(border=True):
        col1, col2 = st.columns([2,3])
        with col1:
            if (current_user["genero"] == "M"):
                st.image(M,f"{current_user["nombre"]}", width=200)
            else:
                st.image(F,f"{current_user["nombre"]}", width=200)
        with col2:
            # st.caption(f"Rating Votado {current_user["rating"]:.1f} ⭐ ({current_user["votos"]:,} votos)")
            st.markdown(f"## {current_user["nombre"]}")
            st.write(f":material/mail: {current_user["email"]}")
            st.write(f":material/explore_nearby: {current_user["provincia"]}")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Rating Promedio ⭐", f"{current_user["rating"]:.1f}")
            with col2:
                st.metric("Numero de votos realizados", f"{current_user["votos"]:,.0f}")

with c2:
    with st.container(border=True):
        col1,col2 = st.columns([1, 3])
        with col1:
            st.image(logo)
            
        with col2:
            st.markdown("### UNIVERSIDAD AUTONOMA DE LOS ANDES")
            st.markdown("### **UNIANDES**")
            st.markdown("#### Seminario Complexivo de Titulación")
            st.caption("Noviembre 2025")
            
            st.markdown("## Sistema de Recomendación de Peliculas")
            st.caption("CASO DE ESTUDIO")

            st.markdown("**Autores:** `Hugo Herrera` | `Jorge López` | `Jaime Borja` | GRUPO 8")