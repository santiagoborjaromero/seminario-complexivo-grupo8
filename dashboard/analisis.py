import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

from dashboard.funciones import load_data, get_dynamic_columns, get_poster_url, api, apiPost

# Define las rutas a los archivos de datos procesados
BASE_DIR = os.getcwd() 
DEFAULT_POSTER = os.path.join(BASE_DIR, 'images', 'default.png')

def main():
    # --------------------------------------
    # Genres, consulta 
    # --------------------------------------
    resp_genres = api("/data/genres")
    if resp_genres is None:
        resp_genres = []
    
    status = resp_genres.get("status", False)
    if status == False:
        st.error("Genres no disponible")
        return
    
    genre_data = json.loads(resp_genres.get("data", False))
    genre_columns = []
    for gen in genre_data:
        genre_columns.append(gen["genre"])
        
    #  Gráficos de Popularidad.
    st.markdown("#### Visualizaciones de Popularidad")
    
    # --------------------------------------
    # Objetos
    # --------------------------------------
    
    #  Crea el panel lateral para los filtros.
    st.sidebar.title("Análisis de Datos")
    st.sidebar.header("Filtros Interactivos")
    selected_genres = st.sidebar.multiselect(
        "Elige los Géneros:", options=sorted(genre_columns), default=[] 
    )
    count_slider = st.sidebar.slider(
        "Popularidad en votos:", 0.0, 68000.0, (30000.0, 68000.0) # tupla (min, max) para definir un rango
    )
    # Agrega una sección para seleccionar el orden de los resultados.
    sort_by = st.sidebar.radio(
        "Elegir orden:",
        ["Rating", "Popularidad"],
        index=0 # Por defecto, ordena por Puntaje
    )
    parameters = {
        "order_by": sort_by,
        "genres": selected_genres,
        "rating_min": 0.0,
        "rating_max": 5.0,
        "items_per_page": 68000,
        "count_slider_min": count_slider[0],
        "count_slider_max": count_slider[1],
        "movie_title": ""
    }
    
    # --------------------------------------
    # Traer el listado de Movies con los filtros seleccionados 
    # --------------------------------------
    df_procesado = apiPost("/data/clean_movies", parameters)
    status = df_procesado.get("status", False)
    message = df_procesado.get("message", False)
    if status == False:
        st.warning("La lista de películas está vacia")
        st.error(f"{message}")
        return
    
    df_procesado = json.loads(df_procesado.get("data", False))
 
    col_categoricas = message.split(",")
    df_filtrado = pd.DataFrame(df_procesado, columns=col_categoricas)
    df_filtrado.reset_index(level=0, inplace=True)
    
    genre_columns, year_columns = get_dynamic_columns(df_filtrado)
       
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        # st.markdown("Top 10 Películas (por N° de Calificaciones)")
        # Este gráfico (Top 10) siempre se ordena por 'rating_conteo' x popularidad.
        df_top10_pop = df_filtrado.nlargest(10, 'rating_conteo')
        fig_bar = px.bar(
            df_top10_pop, x='rating_conteo', y='title', orientation='h',
            title='Top 10 Películas más Populares', hover_data=['rating_promedio', 'genres']
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, width='stretch')

    with col_graf2:
        # st.markdown("Rating Promedio vs. Popularidad")
        # Este gráfico de dispersión usa el df_filtrado completo.
        fig_scatter = px.scatter(
            df_filtrado, x='rating_conteo', y='rating_promedio',
            title='Rating vs. Popularidad', hover_data=['title', 'genres'],
            color='rating_promedio', size='rating_conteo' 
        )
        st.plotly_chart(fig_scatter, width='stretch')

    # st.markdown("---")
    # Gráfico usando la matriz pivote de años.
    st.subheader("Evolución del Rating de una Película")
    selected_movie_title = st.selectbox(
        "Selecciona una película para ver su evolución:",
        # Las opciones del selectbox se muestran en el orden seleccionado.
        options=df_filtrado['title'].unique()
    )
    if selected_movie_title:
        movie_data = df_filtrado[df_filtrado['title'] == selected_movie_title].iloc[0]
        evolution_data = movie_data[year_columns][movie_data[year_columns] > 0]
        if not evolution_data.empty:
            df_evo = pd.DataFrame({'Anio': evolution_data.index.astype(int), 'Rating Promedio': evolution_data.values})
            fig_line = px.line(df_evo, x='Anio', y='Rating Promedio', title=f"Evolución: {selected_movie_title}", markers=True)
            st.plotly_chart(fig_line, width='stretch')
        else:
            st.warning(f"No hay datos de evolución de rating para '{selected_movie_title}'.")

    st.markdown("---")
    # Tabla de datos detallada al final.
    st.subheader("Datos Filtrados (Detalle)")
    # Esta tabla muestra los datos ordenados según la selección del radio button.
    st.dataframe(df_filtrado, width='stretch')
    
    
if __name__ == "__main__":
    main()