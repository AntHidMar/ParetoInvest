# --- Imagen base con Java y Python ---
FROM openjdk:17-slim

# --- Instalar Python, pip y curl para Poetry ---
RUN apt-get update && apt-get install -y python3 python3-pip curl && rm -rf /var/lib/apt/lists/*

# --- Instalar Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 -

# --- Añadir Poetry al PATH ---
ENV PATH="/root/.local/bin:$PATH"

# --- Crear directorio de trabajo ---
WORKDIR /app

# --- Copiar código Python y Java (.jar) ---
COPY app_python/ ./app_python/
COPY app_java/ ./app_java/

# --- Copiar archivos de configuración de Poetry ---
COPY pyproject.toml poetry.lock ./

# --- Instalar dependencias Python con Poetry ---
RUN poetry install --no-root --only main

# --- Comando por defecto: ejecutar Python ---
CMD ["poetry", "run", "python", "app_python/main.py"]
