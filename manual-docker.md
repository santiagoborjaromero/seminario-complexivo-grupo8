Dockerfile 
```c
FROM python:3.13-slim

WORKDIR /app

COPY requirements-api.txt .

RUN apt-get update -y && apt-get install -y \
    libgomp1 \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists

RUN pip install -r requirements-api.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```
```c
docker build -t api-peliculas .
docker run -d -p 8000:8000 --name dock-api-peliculas api-peliculas
```
Google Cloud CLI
https://cloud.google.com/sdk/docs/install?hl=es
```
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")

& $env:Temp\GoogleCloudSDKInstaller.exe
```
Configuración 
https://cloud.google.com/sdk/docs/enabling-accessibility-features?hl=es
```c
gcloud auth login
gcloud config set project api-peliculas-g8-uniandes 
gcloud services enable artifactregistry.googleapis.com 
gcloud artifacts repositories create repo-docker-vg --repository-format=docker --location=us-central1
gcloud auth configure-docker us-central-docker.pkg.dev
docker tag dock-api-peliculas us-central1-docker.pkg.dev/api-peliculas-g8-uniandes/repo-docker-vg/api-peliculas
docker push us-central1-docker-pkg.dev
gcloud services enable run.googleapis.com
gcloud run deply dock-api-peliculas --image=us-central1-docker.pkg.dev/api-peliculas-g8-uniandes/repo-docker-vg/api-peliculas:latest --port:8000 --allow-unauthenticated --platform=managed --region=us-central1




docker tag api-videojuegos-seminario us-central1-docker.pkg.dev/api-videojuegos-seminario-2025/repo-docker-vg/api-seminario:latest
docker push us-central1-docker.pkg.dev/api-videojuegos-seminario-2025/repo-docker-vg/api-seminario:latest
gcloud services enable run.googleapis.com
gcloud run deploy api-videojuegos-servicio --image=us-central1-docker.pkg.dev/api-videojuegos-seminario-2025/repo-docker-vg/api-seminario:latest --port=8080 --allow-unauthenticated --platform=managed --region=us-central1
```

