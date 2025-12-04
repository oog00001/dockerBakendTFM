# Usar una imagen base de Python
FROM python:3.12-slim

# Establecer el directorio de trabajo DENTRO del contenedor
WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requisitos e instalar dependencias
# (Se copia solo este primero para aprovechar la caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO el resto del código (main.py, etc.) 
# desde el contexto (codigoPythonPE-main) a /app
COPY . .

# El 'command' en docker-compose.yml anulará este CMD,
# pero es buena práctica tenerlo.
CMD ["python", "main.py"]
