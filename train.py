import pandas as pd
import numpy as np

from sklearn.preprocessing import OneHotEncoder
from sklearn.model_selection import train_test_split

from pipeline.data_saving import guardar_informacion
from sklearn.metrics.pairwise import cosine_similarity

from pipeline.data_loader import load_data
from pipeline.data_saving import guardar_informacion
from pipeline.model_preprocessing import preparar_datos_modelo, dividir_datos
from pipeline.model_saving import guardar_archivos_modelo
from pipeline.model_training import entrenar_y_evaluar_modelo

import os

BASE_DIR = os.getcwd() 
MODEL_DIR = os.path.join(BASE_DIR, "data", "models")
ENCODER_PATH = os.path.join(MODEL_DIR, "onehot_encoder.joblib")
MODEL_PATH = os.path.join(MODEL_DIR, "lgbm_regressor_default.joblib")

if __name__ == "__main__":
    print("---INICIANDO PIPELINE DE ENTRENAMIENTO DE MODELO---")

    movie = load_data("movie_perfil_contenido.csv")
    if movie is not None:
        print("\n---PREPROCESANDO DATOS PARA EL MODELO---")
        X, y, encoder = preparar_datos_modelo(movie)
        
        print("\n---DIVIDIR DATOS (TRAIN/TEST)---")
        X_train, X_test, y_train, y_test = dividir_datos(X, y)
        
        print("\n---ENTRENANDO Y EVALUANDO MODELO---")
        modelo = entrenar_y_evaluar_modelo(
            X_train, X_test, y_train, y_test
        )
        
        print("\n---GUARDANDO ARCHIVOS DEL MODELO---")
        guardar_archivos_modelo(
            modelo, 
            encoder, 
            MODEL_PATH, 
            ENCODER_PATH
        )
        
        print("\n---PIPELINE DE ENTRENAMIENTO TERMINADO---")
    else: 
        print("Error: no se pudo cargar el archivo")
    
    