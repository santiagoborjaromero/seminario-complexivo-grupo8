# Universidad Autónoma de los Andes - Uniandes
**Facultad de Ciencias Mercantiles
Carrera de Ingeniería de Software**      

**Proyecto Seminario Complexivo**

## **Grupo 8**

**AUTORES:**

Hugo Alfredo Herrera Villalva  
Jaime Santiago Borja Romero  
Jorge Luis López Romo

## **Título del Proyecto**

**Construcción de un Sistema de Recomendación Híbrido de Películas.**

![](https://img.shields.io/badge/Version-0.0.1_alpha-orange) 

## **Definición del Problema**

Las recomendaciones de películas no son del todo precisas, ya que no consideran de manera adecuada variables como el sexo y la edad. En consecuencia, algunos géneros cinematográficos tienden a ser menos vistos por determinados grupos de personas.

La desconfianza en las recomendaciones de películas debido a la gran cantidad de opciones y a las reseñas poco fiables, afecta al público objetivo al dificultar la elección de contenido de calidad, haciendo crucial la solución para que los usuarios puedan satisfacer sus necesidades de manera eficiente

## **Descripción del Proyecto**

## **Herramientas Utilizadas**
![](https://img.shields.io/badge/Python-3.13-blue)
![](https://img.shields.io/badge/FastAPI-0.112.0-red) 

## **Instrucciones**

### Proceso Pipeline

Pipeline es un proceso de limpieza de los datasets fuente, que incluye:
1. Depuración de caracteres UNICODE creando un respaldo de los archivos dataset para poder trabajar con ellos, manteniendo la data original aislada.
2.  < Aumentar mas procesos>

Consideraciones especiales

1. Verificar que la carpeta `dataset_source` se encuentren los archivos requeridos para el proceso
2. El directorio de trabajo es `pipeline`
3. El archivo que indica los paths de carpetas para el proceso es `pipeline/src/tools/func.py`, se puede en el mismo contexto aumentar si es necesario
4. Para ejecutar el proceso 
```c
cd pipeline
python pipeline.py
```
5. Para visualizar los logs puede revisar en `pipeline/logs/srhp-{fecha}.log`


# Prueba de diagramas mermaid
```mermaid
graph TD;
    A-->B;
    A-->C;
    B-->D;
    C-->D;
```