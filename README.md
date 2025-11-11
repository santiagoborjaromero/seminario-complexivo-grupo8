# Universidad Autónoma de los Andes - Uniandes
**Facultad de Ciencias Mercantiles** 

**Carrera de Ingeniería de Software**

**Proyecto Seminario Complexivo**

**Grupo 8**

(Noviembre 2025)

**AUTORES:**
- Hugo Alfredo Herrera Villalva  
- Jaime Santiago Borja Romero  
- Jorge Luis López Romo

## Título del Proyecto
**Construcción de un Sistema de Recomendación Híbrido de Películas - SRP**

![](https://img.shields.io/badge/Version-0.0.1_alpha-orange)

## Definición del Problema

## Descripción del Proyecto

## Herramientas Utilizadas

![](https://img.shields.io/badge/Python-3.13-blue) ![](https://img.shields.io/badge/FastAPI-0.112.0-red)
## Módulos desarrollados

## Requisitos previos

- Descargar la data del proyecto de [Kaggle](https://www.kaggle.com/datasets/grouplens/movielens-20m-dataset?select=tag.csv) (movie.csv, rating.csv, tag.csv)
- Python 3.12+
- Clonar el proyecto https://github.com/santiagoborjaromero/seminario-complexivo-grupo8.git
- Git CLI
## Instalación

Clonar el proyecto
```c
git clone https://github.com/santiagoborjaromero/seminario-complexivo-grupo8.git
```
Entrar en el proyecto y crear la carpeta data
```c
cd seminario-complexivo-grupo8
mkdir data
mkdir data/process
```

***Importante**: Copiar la data descargada del proyecto de kaggle dentro de la carpeta data*

Establecer un  entorno virtual de python 
```python 
python -m venv venv   # En casi todas las versiones de python
py -m venv venv   # En versiones actuales
```
Activación del entorno virtual
```c
.\venv\Scripts\activate
```
Actualizar pip
```c
pip install --upgrade pip
```
Instalación de librerías necesarias para la ejecución del proyecto
```c
pip install -r requirements.txt
```
## Secuencia de Ejecución

### `Proceso inicial`
***Importante**: Solo se ejecutará por una sola ocasión*

Gobierno de datos

Gestión de data mediante la metodología **DAMA** (**Data Management Association**) y **DAMA-DMBOK** como marco de referencia de mejores prácticas para la gestión de datos a lo largo de su ciclo de vida.
- **Calidad de los datos:** Define procesos para medir, analizar, mejorar y controlar la calidad de los datos para asegurar su precisión y consistencia.
```c
python main_dama.py
```

Limpieza de archivos
```c
python main_pipeline.py
```

Al no existir base usuarios (csv) se procede a generar usuarios de forma aleatoria a fin de satisfacer el proceso de registro de usuarios en el sistema.
```c
python main_generar_usuarios.py
```

Insumo para presentación del dashboard de calidad de datos
```c
py main_catalogo_dama.py
```

### `Ejecución normal`

Ejecución de API
```c
uvicorn main_api:app --reload
```

Ejecución de dashboard
```c
streamlit run main_dashboard.py
```






