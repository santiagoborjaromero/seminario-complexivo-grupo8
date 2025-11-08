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


# st.write( st.session_state)
    
st.image("images/portada.png", width="stretch")


if (current_user["genero"] == "M"):
    st.sidebar.image(M,f"{current_user["nombre"]}")
else:
    st.sidebar.image(F,f"{current_user["nombre"]}")

st.caption(f"{current_user["rating"]:.1f} ⭐ ({current_user["votos"]:,} votos)")
# # st.image(poster_url, width='stretch', caption=f"{row.rating_promedio:.1f} ⭐ ({row.rating_conteo:,} votos)")
# st.sidebar.write(f"""
#     {current_user["nombre"]}\n 
#     {current_user["email"]}\n
#     {current_user["votos"]}\n
#     {current_user["rating"]}\n
# """)