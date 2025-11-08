import streamlit as st

st.set_page_config(
    page_title="🔥 Mis Películas 🔥",
    page_icon="🎬",#https://docs.streamlit.io/develop/api-reference/navigation/st.page
    layout="wide"
)

def logout():
    st.session_state.logged_in = False
    st.session_state.user_data = {}
    st.rerun()
    
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_data = {}
   
    
if __name__ == "__main__":
    # st.write(st.session_state)
    pages = []
    if st.session_state.logged_in == True:
        pages.append(st.Page("dashboard/acercade.py", title="Acerca de", icon=":material/sell:", default=True))
        pages.append(st.Page("dashboard/peliculas.py", title="Películas", icon=":material/star_outline:"))
        pages.append(st.Page("dashboard/recomendadas_parati.py", title="Recomendadas para Ti", icon=":material/star_outline:"))
        pages.append(st.Page("dashboard/recomendadas_genero.py", title="Top por género", icon=":material/star_outline:"))
        pages.append(st.Page("dashboard/analisis.py", title="Análisis de Datos", icon=":material/area_chart:"))
        pages.append(st.Page(logout, title="Salir", icon=":material/area_chart:"))
        pg = st.navigation(pages, position="top")
    else:
        pages.append(st.Page("dashboard/signin.py", title="Ingreso", icon=":material/login:"))
        pg = st.navigation(pages, position="top")
    
    pg.run()