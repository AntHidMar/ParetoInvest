# --- Imagen base con Java y Python ---
FROM openjdk:17-jdk-slim

# --- Variables de entorno ---
ENV DEBIAN_FRONTEND=noninteractive
ENV QT_QPA_PLATFORM=offscreen
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# --- Instalar dependencias del sistema ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev build-essential curl git \
    libgl1 libglib2.0-0 libx11-6 libxext6 libxrender1 libxcb1 \
    libxkbcommon-x11-0 libdbus-1-3 libssl-dev zlib1g-dev libglu1-mesa-dev \
    libegl1 libgl1-mesa-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Actualizar pip y herramientas de construcción ---
RUN python3 -m pip install --upgrade pip setuptools wheel

# --- Instalar Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN poetry config virtualenvs.in-project true

# --- Crear directorio de trabajo ---
WORKDIR /app

# --- Copiar proyecto completo ---
COPY . /app/ParetoInvest
WORKDIR /app/ParetoInvest

# --- Instalar dependencias con Poetry ---
RUN poetry install --no-interaction --no-root

# --- Comando por defecto para testear o ejecutar ---
CMD ["bash"]
