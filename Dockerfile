# --- Imagen base con Python 3.11 slim ---
FROM python:3.11-slim

# --- Variables de entorno ---
ENV DEBIAN_FRONTEND=noninteractive
ENV QT_QPA_PLATFORM=offscreen
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# --- Instalar JDK17 y librerías necesarias ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jdk \
    build-essential curl git \
    libgl1 libglib2.0-0 libx11-6 libxext6 libxrender1 libxcb1 libxkbcommon-x11-0 libdbus-1-3 \
    libssl-dev zlib1g-dev libglu1-mesa-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Actualizar pip y setuptools ---
RUN python3 -m pip install --upgrade pip setuptools wheel

# --- Instalar PyQt6 directamente desde pip (wheel precompilada) ---
RUN python3 -m pip install PyQt6==6.10.0

# --- Instalar Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 -

# --- Crear directorio de trabajo ---
WORKDIR /app

# --- Copiar proyecto ---
COPY . /app/ParetoInvest

# --- Entrar en la carpeta del proyecto ---
WORKDIR /app/ParetoInvest

# --- Opcional: inspección del entorno ---
RUN poetry env info || true
RUN poetry check || true

# --- Instalar dependencias con Poetry ---
RUN poetry install --no-interaction --no-ansi -vvv

# --- Añadir la raíz al PYTHONPATH (para imports relativos) ---
ENV PYTHONPATH=/app

# --- Comando por defecto ---
CMD ["poetry", "run", "python", "ParetoInvest/main.py"]
