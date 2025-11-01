# main_dashboard.py
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

#  Definición de Rutas 
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # Define la ruta del archivo procesado
DATA_PROCESS_DIR = os.path.join(BASE_DIR, 'data', 'process')
PROCESSED_FILE = os.path.join(DATA_PROCESS_DIR, 'procesados_movies.csv')

#  Funciones de Carga  

@st.cache_data 
def load_data(file_path):
    """
    'load_data' carga el archivo CSV procesado del pipeline usando
     @st.cache_data para optimizar el rendimiento.
    """
    try:
        df = pd.read_csv(file_path, encoding='latin1') 
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo 'procesados_movies.csv' en {file_path}")
        st.info("Por favor, ejecuta primero python main_pipeline.py para generar el archivo de datos procesados.")
        return None

@st.cache_data
def get_dynamic_columns(df):
    """
    La función 'get_dynamic_columns' inspecciona el df y
    extrae las columnas de género y las de año desde (Pivot).
    """
    base_cols = ['movieid', 'title', 'genres', 'rating_promedio', 'rating_conteo', 'tags_agrupados']
    year_cols = [col for col in df.columns if col.isdigit() and len(col) == 4]
    genre_cols = [col for col in df.columns if col not in base_cols and col not in year_cols]
    
    return genre_cols, year_cols

#  Función Principal 
def main():
    """
    Función principal ejecuta Streamlit.
    TODA LA LÓGICA DEBE IR DENTRO DE ESTA FUNCIÓN.
    """
    st.markdown("Versión V1.0: Visualizando los datos de `procesados_movies.csv`.")

    # Carga los datos 
    df_procesado = load_data(PROCESSED_FILE)
    
    if df_procesado is None:
        return
 
    # Llama a la función helper para obtener las listas de columnas
    genre_columns, year_columns = get_dynamic_columns(df_procesado)

    #  Barra Lateral (Filtros) 
    st.sidebar.header("Filtros Interactivos")

    # Crea un widget géneros
    selected_genres = st.sidebar.multiselect(
        "Elige los Géneros:",
        options=sorted(genre_columns), # Usa de género dinámicamente
        default=[] 
    )

    # Crea un widget  rango de rating
    rating_slider = st.sidebar.slider(
        "Filtro por Rating Promedio:",
        min_value=0.0,
        max_value=5.0,
        value=(0.0, 5.0) # tupla (min, max) para definir un rango
    )

    # Crea un slider para la popularidad basado en 'rating_conteo'
    min_ratings_limit = int(df_procesado['rating_conteo'].quantile(0.75))
    total_ratings_slider = st.sidebar.slider(
        "Filtro por Calificaciones:",
        min_value=0,
        max_value=int(df_procesado['rating_conteo'].max()),
        value=min_ratings_limit
    ) 

    #  Filtrado del DataFrame 
    
    df_filtrado = df_procesado.copy() # copia del df completo
    
    # Aplica el filtro de Rating Promedio basado en el slider con tupla (min_valor, max_valor)
    df_filtrado = df_filtrado[
        (df_filtrado['rating_promedio'] >= rating_slider[0]) &
        (df_filtrado['rating_promedio'] <= rating_slider[1])
    ]

    # Aplica el filtro de Total de Ratings basado en el slider
    df_filtrado = df_filtrado[
        df_filtrado['rating_conteo'] >= total_ratings_slider
    ]

    
    if selected_genres:  # se ejecuta cuando se seleccionado un género
        for genre in selected_genres:
            df_filtrado = df_filtrado[df_filtrado[genre] == 1] #usa los 1 para filtrar usando el la separacion de los generos
            
    #  Visualización 
    
    st.header("Resultados del Análisis")
    col1, col2 = st.columns(2)
    col1.metric("Películas Encontradas", f"{len(df_filtrado):,}")
    col2.metric("Total Películas en BD", f"{len(df_procesado):,}")
    st.markdown("---")
    
    # --- Visualizaciones con Plotly ---
    # Comprueba si el dataframe filtrado NO está vacío antes de intentar dibujar
    if not df_filtrado.empty:
        st.subheader("Visualizaciones de Popularidad")

        # Crea dos columnas para los gráficos
        col_graf1, col_graf2 = st.columns(2)

        with col_graf1:
            #  Top 10 Películas por Popularidad por 'rating_conteo'
            st.markdown("#### Top 10 Películas (por N° de Calificaciones)")
            df_top10 = df_filtrado.nlargest(10, 'rating_conteo')
            fig_bar = px.bar(
                df_top10, x='rating_conteo', y='title', orientation='h',
                title='Top 10 Películas más Populares', hover_data=['rating_promedio', 'genres']
            )
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_graf2:
            # Relación entre Rating y Popularidad
            st.markdown("#### Rating Promedio vs. Popularidad")
            fig_scatter = px.scatter(
                df_filtrado, x='rating_conteo', y='rating_promedio',
                title='Rating vs. Popularidad', hover_data=['title', 'genres'],
                color='rating_promedio', size='rating_conteo' 
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        #  GRÁFICO DE EVOLUCIÓN 
        st.markdown("---")
        st.subheader("Evolución del Rating de una Película") # Usando tu Matriz Pivote de Años 
        
        selected_movie_title = st.selectbox(
            "Selecciona una película para ver su evolución:",
            options=df_filtrado['title'].unique() # widget  que elege película del DataFrame filtrado
        ) 
        
        if selected_movie_title:
            movie_data = df_filtrado[df_filtrado['title'] == selected_movie_title].iloc[0] # Extrae la fila completa de la película
            evolution_data = movie_data[year_columns] # Toma solo las columnas de año del pivote
            evolution_data = evolution_data[evolution_data > 0] # Filtra los años donde el rating no sea 0 
            
            if not evolution_data.empty:
                # Convierte los datos de la serie a un DataFrame para Plotly
                df_evo = pd.DataFrame({
                    'Anio': evolution_data.index.astype(int),
                    'Rating Promedio': evolution_data.values
                })
                # Crea el gráfico de líneas
                fig_line = px.line(
                    df_evo, x='Anio', y='Rating Promedio',
                    title=f"Evolución del Rating para: {selected_movie_title}", markers=True
                )
                fig_line.update_xaxes(type='linear') # Asegura que el eje X sea numérico
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.warning(f"No hay datos de evolución de rating para '{selected_movie_title}'.")
        
    else:
        st.warning("No se encontraron películas con los filtros seleccionados.")

    
    st.subheader("Datos Filtrados (Detalle)")
    st.dataframe(df_filtrado, use_container_width=True) # Muestra el DataFrame filtrado


if __name__ == "__main__":
    main()