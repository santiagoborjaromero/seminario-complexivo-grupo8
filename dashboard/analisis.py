import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard.funciones import load_data, get_dynamic_columns


PROCESSED_FILE = 'procesados_movies.csv'

df_procesado = load_data(PROCESSED_FILE)
if df_procesado is None:
    exit(0)

genre_columns, year_columns = get_dynamic_columns(df_procesado)
df_filtrado = df_procesado.copy()

if df_filtrado.empty:
    st.warning("No hay datos para analizar con los filtros seleccionados.")
else:
    #  Gráficos de Popularidad.
    st.markdown("#### Visualizaciones de Popularidad")
    
    
    #  Crea el panel lateral para los filtros.
    st.sidebar.title("Análisis de Datos")
    st.sidebar.header("Filtros Interactivos")
    selected_genres = st.sidebar.multiselect(
        "Elige los Géneros:", options=sorted(genre_columns), default=[] 
    )
    # rating_slider = st.sidebar.slider(
    #     "Filtro por Rating Promedio:", 0.0, 5.0, (0.0, 5.0) # tupla (min, max) para definir un rango
    # )
    min_ratings_limit = int(df_procesado['rating_conteo'].quantile(0.75))
    total_ratings_slider = st.sidebar.slider(
        "Filtro por Calificaciones:", 0, int(df_procesado['rating_conteo'].max()), min_ratings_limit
    ) 

    # Agrega una sección para seleccionar el orden de los resultados.
    st.sidebar.header("Ordenar Resultados Por:")
    sort_by = st.sidebar.radio(
        "Elegir orden:",
        ["Puntaje (Mejor Calificadas)", "Popularidad (Más Votadas)"],
        index=0 # Por defecto, ordena por Puntaje
    )
    
    #  Aplica los filtros de la barra lateral al DataFrame.
    df_filtrado = df_procesado.copy()
    df_filtrado = df_filtrado[
        (df_filtrado['rating_promedio'] >= 1) &
        (df_filtrado['rating_promedio'] <= 5)
    ]
    df_filtrado = df_filtrado[
        df_filtrado['rating_conteo'] >= total_ratings_slider
    ]
    if selected_genres:
        for genre in selected_genres:
            df_filtrado = df_filtrado[df_filtrado[genre] == 1]
    
    # Ordena el df_filtrado según la selección de 'sort_by'.
    if sort_by == "Popularidad (Más Votadas)":
        df_filtrado = df_filtrado.sort_values(by='rating_conteo', ascending=False)
        sort_label = "Popularidad"
    else: # "Puntaje (Mejor Calificadas)"
        df_filtrado = df_filtrado.sort_values(by='rating_promedio', ascending=False)
        sort_label = "Puntaje"

        
    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.markdown("Top 10 Películas (por N° de Calificaciones)")
        # Este gráfico (Top 10) siempre se ordena por 'rating_conteo' x popularidad.
        df_top10_pop = df_filtrado.nlargest(10, 'rating_conteo')
        fig_bar = px.bar(
            df_top10_pop, x='rating_conteo', y='title', orientation='h',
            title='Top 10 Películas más Populares', hover_data=['rating_promedio', 'genres']
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, width='stretch')

    with col_graf2:
        st.markdown("Rating Promedio vs. Popularidad")
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