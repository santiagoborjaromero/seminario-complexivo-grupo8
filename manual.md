
# Trabajo en clase
2025-10-18

Crear entorno virtual
```bash
python -m venv venv
```
Activar entonrno virtual
```bash
.\venv\Scripts\activate
```
Desactivar entonrno virtual
```bash
deactivate
```
Respaldo inicial de librerias y eso se realiza cada vez que se instala alguna libreria
```bash
pip freeze > requirements.txt
```
Para instalar las librerias desde el archivo requirements.txt
```bash
pip install -r requirements.txt
```
Actualizar pip
```bash
pip install --upgrade pip
```
## Librerias  
pandas, streamlit, seaborn, fastapi, numpy, matplot.pyplot
```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter
pip install missingno
pip freeze > requirements.txt
```
# A Trabajar
Creamos un branch por cada cosa que hagamos
```bash
git checkout -b feature/data-loader
```
***NOTA:** esto crea un nuevo branch ej:`feature/data-loader` y copia todo lo del branch **master** para que pueda programar o modificar* 

