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
# MEMORIA TÉCNICA
## Sistema de Recomendación Híbrido de Películas - MovieMatch


## 1. TÍTULO DEL PROYECTO Y MIEMBROS

### Título del Proyecto
**Construcción de un Sistema de Recomendación Híbrido de Películas**


---

## 2. DEFINICIÓN DEL PROBLEMA

Los sistemas tradicionales de recomendación de películas presentan limitaciones significativas al depender de un único enfoque: algunos se basan únicamente en similitud temática, mientras que otros solo consideran opiniones de usuarios similares. Esto resulta en recomendaciones imprecisas y homogéneas que no reflejan completamente las preferencias del usuario.

El desafío es construir un sistema inteligente que combine múltiples estrategias analíticas para ofrecer recomendaciones más precisas, personalizadas y relevantes, mejorando significativamente la experiencia del usuario final en plataformas de streaming y consumo de contenido audiovisual.

---

## 3. OBJETIVO PRINCIPAL

Desarrollar e implementar un sistema de recomendación híbrido que integre filtrado basado en contenido con filtrado colaborativo para generar recomendaciones personalizadas de películas que consideren tanto similitud temática como preferencias de usuarios con gustos similares, proporcionando a cada usuario un ranking de películas relevantes con explicaciones de las razones de la recomendación.

---

## 4. COLUMNAS CLAVE DEL DATASET

El proyecto utiliza el dataset **MovieLens 20M**, que contiene información estructurada en tres archivos principales:

### Dataset: rating.csv
1. **userId** - Identificador único del usuario. Fundamental para identificar patrones de preferencia y crear perfiles colaborativos.
2. **movieId** - Identificador único de la película. Crítico para mapear ratings a películas específicas.
3. **rating** - Calificación numérica (escala 0.5 a 5.0). Variable target principal para entrenar el modelo colaborativo.
4. **timestamp** - Marca temporal de la calificación. Útil para análisis temporal y validación de datos.

### Dataset: movie.csv
5. **title** - Nombre de la película. Esencial para presentación al usuario final.
6. **genres** - Géneros asociados (ej: Drama|Action). Componente clave para crear perfiles de contenido y calcular similitud temática.

### Dataset: tag.csv
7. **tag** - Etiquetas descriptivas asignadas por usuarios (ej: "cinematography", "plot twist"). Complementan géneros para crear perfiles de contenido más ricos y matizados.

---

## 5. RESPONSABILIDADES DE LOS COMPONENTES DE LA ARQUITECTURA

### 5.1 PIPELINE DE DATOS

El pipeline prepara y procesa los datos para generar modelos entrenados.

**Responsabilidades principales:**

- **Carga y Limpieza de Datos**: 
  - Carga CSV de ratings, películas y tags desde MovieLens 20M
  - Elimina filas con datos faltantes o inconsistentes
  - Valida que movieId y userId correspondan entre archivos
  - Filtra registros con ruido o valores atípicos

- **Creación de Perfiles de Contenido**:
  - Combina géneros y tags para cada película en un perfil textual
  - Aplica TF-IDF (Term Frequency-Inverse Document Frequency) para vectorizar perfiles
  - Calcula matriz de similitud coseno entre películas
  - Guarda matriz de similitud en pickle para acceso rápido

- **Entrenamiento del Modelo Colaborativo**:
  - Prepara matriz usuario-película con ratings
  - Entrena algoritmo SVD (Singular Value Decomposition) usando librería Surprise
  - Realiza validación cruzada para evaluar performance
  - Guarda modelo entrenado para predicciones en tiempo real

- **Validación y Guardado de Artefactos**:
  - Valida calidad de datos en cada etapa
  - Guarda matriz de similitud de contenido (artefacto 1)
  - Guarda modelo colaborativo entrenado (artefacto 2)
  - Genera reportes de estadísticas (mediana, desviación estándar)

### 5.2 API REST (FastAPI)

Interfaz programática que sirve recomendaciones a través de endpoints HTTP.

**Responsabilidades principales:**

- **Endpoint `/recommendations/hybrid/{user_id}`**:
  - Recibe ID de usuario como parámetro
  - Ejecuta proceso de dos etapas: (1) Filtrado colaborativo genera 50 películas candidatas con predicción alta, (2) Re-ranking potencia películas similares a favoritas del usuario (5 estrellas)
  - Retorna top 10 con explicación de recomendación
  - Maneja errores y validaciones de entrada

- **Endpoints de Datos Complementarios**:
  - `/users/{user_id}/rated-movies`: Retorna películas mejor calificadas por usuario
  - `/movies/{movie_id}/similar`: Retorna películas similares por contenido
  - `/recommendations/by-genre/{genre}`: Recomendaciones filtradas por género

- **Autenticación y Seguridad**:
  - Valida usuarios existentes en dataset
  - Previene acceso no autorizado
  - Maneja excepciones y logging

### 5.3 DASHBOARD (Streamlit)

Interfaz web interactiva para consumo visual de recomendaciones.

**Responsabilidades principales:**

- **Login y Selección de Usuario**:
  - Sidebar con selector de user_id disponibles
  - Autenticación básica
  - Sesiones de usuario persistentes

- **Visualización de Preferencias Previas**:
  - Tabla de películas con ratings más altos (5, 4.5 estrellas)
  - Géneros favoritos del usuario
  - Estadísticas de visualización

- **Visualización de Top 10 Recomendaciones Híbridas**:
  - Card interactiva para cada película recomendada
  - Explicación clara: "Porque te gustó [película similar] y a usuarios como tú les encantó [película recomendada]"
  - Información: título, géneros, rating predicho
  - Botones para más detalles o similar movies

---

## 6. ARQUITECTURA TÉCNICA Y FLUJO GENERAL

```
┌─────────────────────────────────────────────────────────────────┐
│                     MOVIELENS 20M DATASET                       │
│              (ratings.csv, movies.csv, tags.csv)                │
└────────────────────┬────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PIPELINE (Python)                             │
├─────────────────────────────────────────────────────────────────┤
│ • Data Loader: Carga y validación inicial                       │
│ • Data Processing: Limpieza y transformación                    │
│ • Content-Based: TF-IDF + Similitud Coseno                      │
│ • Collaborative: SVD (Surprise library)                         │
│ • Model Saving: Pickle para API consumption                     │
└────────────────────┬──────────────────┬──────────────────────────┘
                     │                  │
        ┌────────────▼────────┐    ┌────▼──────────────┐
        │ Similarity Matrix   │    │ Trained SVD Model │
        │ (Content-based)     │    │ (Collaborative)   │
        └────────────┬────────┘    └────┬──────────────┘
                     │                  │
                     └──────────┬───────┘
                                ▼
        ┌───────────────────────────────────────────┐
        │         API (FastAPI + Uvicorn)          │
        │  /recommendations/hybrid/{user_id}       │
        │  /users/{user_id}/rated-movies           │
        │  /movies/{movie_id}/similar              │
        └───────────────┬───────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────────┐
        │   Dashboard (Streamlit)                   │
        │  • Login & User Selection                 │
        │  • Rated Movies Display                   │
        │  • Top 10 Hybrid Recommendations          │
        │  • Explanations & Similar Movies          │
        └───────────────────────────────────────────┘
```

---

## 7. FLUJO DEL PIPELINE (main_pipeline.py)

### Paso 1: Carga de Datos
```
data_loader.py
├─ Lee rating.csv
├─ Lee movie.csv
├─ Lee tag.csv
└─ Retorna DataFrames validados
```

### Paso 2: Procesamiento y Limpieza
```
data_process.py
├─ Elimina filas duplicadas
├─ Maneja valores faltantes (NaN)
├─ Valida tipos de datos
├─ Filtra outliers en ratings
└─ Guarda datos limpios en CSV
```

### Paso 3: Procesamiento Específico de Datos
```
dama_movie_process.py
├─ Extrae géneros y los divide
├─ Mapea movieId a información película
└─ Prepara estructura para TF-IDF

dama_tag_process.py
├─ Agrupa tags por película
├─ Realiza limpieza de texto
└─ Combina con géneros

dama_rating_process.py
├─ Estructura matriz usuario-película
├─ Calcula estadísticas (media, mediana, desv. est.)
└─ Prepara formato para Surprise
```

### Paso 4: Creación de Perfiles (TF-IDF)
```
Perfiles de Contenido:
├─ Película 1: "drama action thriller cinematography plot"
├─ Película 2: "comedy romance plot twist"
└─ Película N: "..."
     ▼
TF-IDF Vectorization:
├─ Convierte cada perfil a vector numérico
├─ Calcula importancia de términos
└─ Genera matriz término-película

Similitud Coseno:
├─ Compara vectores de películas
├─ Calcula matriz NxN (N = número de películas)
└─ Valor 1.0 = máxima similitud, 0.0 = nada similar
```

### Paso 5: Entrenamiento del Modelo Colaborativo
```
model_preprocessing.py
├─ Prepara datos para Surprise
├─ Define escala de ratings (0.5 - 5.0)
└─ Divide train/test (80-20)

model_training.py
├─ Instancia SVD (Singular Value Decomposition)
├─ Entrena en datos de training
├─ Valida con cross-validation
└─ Guarda modelo en pickle

Resultado: Modelo que predice rating usuario-película no vista
```

### Paso 6: Guardado de Artefactos
```
model_saving.py
├─ Guarda modelo SVD entrenado → model.pkl
└─ Guarda configuración del modelo

data_saving.py
├─ Guarda matriz de similitud → similarity_matrix.pkl
└─ Guarda información de películas → movies_info.csv
```

---

## 8. IMPLEMENTACIÓN DEL API (FastAPI)

### Estructura
```
api/
├─ main.py (Punto de entrada)
├─ routers/
│  ├─ auth.py (Autenticación)
│  ├─ data.py (Datos de películas y usuarios)
│  └─ recomendation.py (Recomendaciones híbridas)
├─ models/
│  ├─ usuario.py (Schema Usuario)
│  └─ movie_form_data.py (Schema Película)
├─ schemas/
│  └─ schema_user.py (Validación de entrada)
└─ utils/
   └─ funciones.py (Funciones auxiliares)
```

### Endpoint Principal: `/recommendations/hybrid/{user_id}`

**Lógica:**

1. **Validar Usuario**: Verifica que user_id existe en dataset
2. **Obtener Películas Calificadas por Usuario**: Películas con ratings >= 5.0 (favoritas)
3. **Filtrado Colaborativo (Etapa 1)**:
   - Usa modelo SVD para predecir ratings de películas no vistas
   - Ordena por predicción descendente
   - Selecciona top 50 candidatos
4. **Filtrado Basado en Contenido (Etapa 2 - Re-ranking)**:
   - Para cada película candidata, calcula similitud con favoritas del usuario
   - Aplica pesos: película es mejor si es temáticamente similar a favoritas
   - Nueva puntuación = 0.6 * predicción_colaborativa + 0.4 * similitud_contenido
5. **Retorna Top 10** con explicación

---

## 9. IMPLEMENTACIÓN DEL DASHBOARD (Streamlit)

### Navegación Principal
```
Sidebar:
├─  Dashboard (página principal)
├─  Mis Películas (favoritas del usuario)
├─  Análisis (estadísticas)
├─  Recomendadas (top 10 híbridas)

```

### Flujo de Usuario
1. **Inicio**: Usuario selecciona su user_id del dropdown
2. **Autenticación**: Sistema valida que el usuario existe
3. **Dashboard Principal**: 
   - Bienvenida personalizada
   - Top películas calificadas por usuario
   - Estadísticas rápidas (total calificaciones, promedio rating)
4. **Recomendaciones**:
   - Consulta API endpoint
   - Muestra top 10 con cards interactivas
   - Cada card contiene: póster (si aplica), título, géneros, rating predicho, explicación
   - Opción para ver películas similares

---

## 10. TECNOLOGÍAS UTILIZADAS

### Backend
- **Python 3.x**: Lenguaje principal de desarrollo
- **FastAPI**: Framework web moderno para API REST
- **Uvicorn**: Servidor ASGI para FastAPI
- **Pandas**: Manipulación y análisis de datos
- **Scikit-learn**: TF-IDF y cálculo de similitud
- **Surprise**: Algoritmos de filtrado colaborativo (SVD)
- **Pickle**: Serialización de modelos y matrices

### Frontend
- **Streamlit**: Framework para dashboard interactivo
- **Python**: Lógica de visualización

### Infraestructura
- **Docker**: Contenedorización (opcional, para despliegue)
- **GitHub**: Control de versiones

### Librerías Complementarias
- **NumPy**: Operaciones numéricas
- **Requests**: Consultas HTTP desde dashboard a API
- **Python-multipart**: Manejo de formularios en API

---

## 11. CONCEPTO DE MEDIANA Y DESVIACIÓN ESTÁNDAR

### Mediana
En el contexto del proyecto, la mediana es utilizada para:
- **Valor Central**: Representa el rating central de preferencias de un usuario sin sesgo de extremos
- **Robustez**: No se ve afectada por ratings muy altos o muy bajos (outliers)
- **Ejemplo**: Si un usuario calificó 5 películas con ratings [1, 2, 5, 5, 5], la mediana es 5 (valor central), mejor representación que media=3.4

### Desviación Estándar
En el contexto del proyecto:
- **Variabilidad**: Mide cuánto varían los ratings de un usuario respecto a su promedio
- **Consistencia**: Desv. Est. baja = usuario tiene gustos consistentes, Desv. Est. alta = usuario es versátil
- **Validación de Datos**: Ayuda a detectar anomalías en patrones de calificación
- **Ejemplo**: Usuario A (ratings: [4, 4, 4, 4, 5]) vs Usuario B (ratings: [1, 2, 4, 5, 5])
  - Usuario A: Desv. Est. baja = gustos consistentes
  - Usuario B: Desv. Est. alta = gustos variados

---

## 12. PROCESO DE LIMPIEZA DE DATOS

### Criterios de Eliminación
1. **Valores Faltantes (NaN)**:
   - Si userId, movieId o rating son NaN → se elimina la fila
   - Si información de película (título, género) falta → se marca para validación

2. **Datos Inconsistentes**:
   - movieId en ratings.csv que no existe en movies.csv → se elimina
   - Rating fuera de rango [0.5, 5.0] → se marca como outlier o se elimina

3. **Ruido y Outliers**:
   - Usuarios con una sola calificación (posible bot o ruido)
   - Películas con muy pocas calificaciones (< 5) → útiles solo para filtrado colaborativo

4. **Duplicados**:
   - Mismo usuario calificando misma película múltiples veces → se mantiene el más reciente

### Resultados de Limpieza
- Dataset original: ~20M ratings
- Después de limpieza: [X] ratings válidos (depende del script data_process.py)
- Pérdida de datos: ~[%] (mínima, ya que dataset es limpio)

---

## 13. MODELADO Y TÉCNICAS UTILIZADAS

### Filtrado Basado en Contenido (Content-Based Filtering)

**Técnica: TF-IDF + Similitud Coseno**

1. **TF-IDF (Term Frequency - Inverse Document Frequency)**:
   - Convierte perfiles textuales (géneros + tags) de películas a vectores numéricos
   - TF: Frecuencia del término en el documento
   - IDF: Importancia inversa del término en todos los documentos
   - Resultado: Vector donde términos raros y relevantes tienen peso alto

2. **Similitud Coseno**:
   - Calcula ángulo entre dos vectores
   - Valor 1.0 = películas idénticas, 0.0 = completamente diferentes
   - Ejemplo: Si Usuario gustó de "Matrix", se recomiendan películas similares a Matrix

### Filtrado Colaborativo (Collaborative Filtering)

**Técnica: SVD (Singular Value Decomposition)**

1. **Matriz Usuario-Película**:
   - Filas = Usuarios, Columnas = Películas, Valores = Ratings
   - Matriz dispersa (mayoría de celdas vacías)

2. **SVD**:
   - Factoriza matriz grande en tres matrices más pequeñas
   - Descubre factores latentes: "Géneros preferidos", "Intensidad de acción", etc.
   - Predice ratings faltantes basado en factores latentes

3. **Predicción**:
   - Para usuario X y película Y no calificada
   - SVD predice qué calificación daría usuario X
   - Formato: rating_predicho = 0.0 a 5.0

### Combinación Híbrida (Re-ranking)

**Fórmula de Re-ranking:**
```
puntuación_final = 0.6 * rating_predicho_colaborativo 
                 + 0.4 * similitud_contenido_con_favoritas
```

- **60% Colaborativo**: Considera gustos de usuarios similares
- **40% Contenido**: Considera similitud temática con preferencias demostradas
- **Balance**: Captura tanto descubrimiento (colaborativo) como relevancia (contenido)

---

## 14. RESULTADOS Y MÉTRICAS

### Métricas de Evaluación

1. **RMSE (Root Mean Squared Error)** en modelo SVD:
   - Mide precisión de predicciones colaborativas
   - Valores típicos: 0.7 - 1.0 (escala 0.5 - 5.0)

2. **Precisión de Recomendación**:
   - % de top 10 recomendaciones que usuario encontró relevantes
   - Evaluado mediante feedback implícito (si usuario consulta película recomendada)

3. **Cobertura**:
   - % de películas que pueden ser recomendadas a al menos un usuario

### Utilidad de la Herramienta

1. **Para Usuarios**:
   - Descubren películas relevantes sin explorar manualmente
   - Explicaciones claras de "por qué" se recomiendan
   - Balance entre similitud y novedad

2. **Para Plataformas**:
   - Aumenta engagement y retención de usuarios
   - Mejora experiencia personalizada
   - Datos para optimización futura

---

## 15. METODOLOGÍAS Y TÉCNICAS DE DESARROLLO

### Control de Versiones
- **Git + GitHub**: Repositorio seminario-complexivo-grupo8
- **Commits frecuentes**: Seguimiento de cambios
- **Branches**: main (producción), develop (desarrollo)
- **README.md**: Documentación de uso y estructura

### Desarrollo Ágil
- **Iteraciones cortas**: Sprints de 1-2 semanas
- **Revisiones**: Code review entre miembros del equipo
- **Integración continua**: Testing automático (si aplica)

### Modularización
- **Separación de concerns**: Pipeline, API, Dashboard independientes
- **Scripts reutilizables**: data_loader, data_process, etc.
- **Configuración externalizada**: Variables de entorno

### Documentación
- **Docstrings**: En funciones clave
- **README técnico**: Instrucciones de instalación y ejecución
- **Comentarios**: En lógica compleja
- **Esta memoria técnica**: Guía integral del proyecto

### Testing
- **Validación de datos**: En cada etapa del pipeline
- **Manejo de errores**: Try-catch en API endpoints
- **Logs**: Registro de operaciones importantes

---

## 16. CONCLUSIONES Y APRENDIZAJES

### Logros
- Sistema funcional que combina dos técnicas complementarias
- API REST escalable y fácil de consumir
- Dashboard intuitivo para usuarios finales
- Pipeline automatizado y reproducible

### Aprendizajes Técnicos
- TF-IDF y similitud coseno para análisis de contenido
- Algoritmos de factorización de matrices (SVD) para predicción
- Diseño de APIs REST con FastAPI
- Desarrollo de dashboards interactivos con Streamlit
- Buenas prácticas en versionado y documentación

### Posibles Mejoras Futuras
1. **Escalabilidad**: Implementar caché (Redis) para predicciones frecuentes
2. **Modelos Avanzados**: Deep Learning (Neural Collaborative Filtering)
3. **Realtime**: WebSockets para actualizaciones en vivo
4. **Feedback**: Sistema de valoración de recomendaciones para reentrenamiento
5. **Diversidad**: Algoritmos para evitar "filter bubbles" y burbuja de contenido

---

## 17. REFERENCIAS Y RECURSOS

1. **Dataset**: MovieLens 20M - https://www.kaggle.com/datasets/grouplens/movielens-20m-dataset
2. **FastAPI**: https://fastapi.tiangolo.com/
3. **Streamlit**: https://streamlit.io/
4. **Surprise Library**: https://surprise.readthedocs.io/
5. **Scikit-learn**: https://scikit-learn.org/
6. **Hybrid Recommendation Systems**: Artículos y papers de investigación en sistemas híbridos

---

## 18. ANEXOS

### A. Estructura de Directorios
```
seminario-complexivo-grupo8/
├─ pipeline/
│  ├─ data_loader.py
│  ├─ data_process.py
│  ├─ dama_movie_process.py
│  ├─ dama_tag_process.py
│  ├─ dama_rating_process.py
│  ├─ model_preprocessing.py
│  ├─ model_training.py
│  ├─ model_saving.py
│  ├─ data_saving.py
│  └─ main_pipeline.py
├─ api/
│  ├─ main.py
│  ├─ routers/
│  │  ├─ auth.py
│  │  ├─ data.py
│  │  └─ recomendation.py
│  ├─ models/
│  │  ├─ usuario.py
│  │  └─ movie_form_data.py
│  ├─ schemas/
│  │  └─ schema_user.py
│  ├─ utils/
│  │  └─ funciones.py
│  └─ main_api.py
├─ dashboard/
│  ├─ dama.py
│  ├─ signin.py
│  ├─ peliculas.py
│  ├─ recomendadas_parati.py
│  ├─ recomendadas_genero.py
│  ├─ analisis.py
│  ├─ acercade.py
│  ├─ funciones.py
│  └─ main_dashboard.py
├─ data/
│  ├─ ratings.csv
│  ├─ movies.csv
│  └─ tags.csv
├─ models/
│  ├─ model.pkl (modelo SVD entrenado)
│  └─ similarity_matrix.pkl (matriz de similitud)
├─ .gitignore
├─ README.md
└─ requirements.txt
```

### B. Dependencias (requirements.txt)
```
pandas==1.3.0
scikit-learn==0.24.0
surprise==0.1
fastapi==0.68.0
uvicorn==0.15.0
streamlit==0.86.0
numpy==1.21.0
requests==2.26.0
python-multipart==0.0.5
```

---

**Documento preparado para defensa de graduación**  
**Fecha**: Noviembre 2025  
**Versión**: 1.0  
**Estado**: Completo






