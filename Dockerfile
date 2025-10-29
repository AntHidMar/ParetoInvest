# --- Base: Python 3.11 + OpenJDK 17 ---
FROM python:3.11-slim

# --- Variables de entorno ---
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV QT_QPA_PLATFORM=offscreen
ENV PATH="/root/.local/bin:$PATH"

# --- Instalar dependencias de compilación y GUI ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git \
    openjdk-17-jdk-headless \
    libgl1 libegl1 libglib2.0-0 libx11-6 libxext6 libxrender1 \
    libxcb1 libxkbcommon-x11-0 libdbus-1-3 \
    libssl-dev zlib1g-dev libglu1-mesa-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Actualizar pip, setuptools y wheel ---
RUN python -m pip install --upgrade pip setuptools wheel

# --- Instalar Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 -

# --- Crear directorio de trabajo ---
WORKDIR /app

# --- Copiar proyecto ---
COPY . /app/ParetoInvest

# --- Configurar Poetry para virtualenv dentro del proyecto ---
WORKDIR /app/ParetoInvest
RUN poetry config virtualenvs.in-project true

# --- Instalar dependencias Python (PyQt6 incluido) ---
RUN poetry install --no-interaction --no-root

# --- Añadir PYTHONPATH para imports relativos ---
ENV PYTHONPATH=/app

# --- Comando por defecto ---
CMD ["poetry", "run", "python", "ParetoInvest/main.py", "--help"]
