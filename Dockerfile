# --- Imagen base oficial de Python 3.11 ---
FROM python:3.11-slim

# --- Variables de entorno ---
ENV DEBIAN_FRONTEND=noninteractive
ENV QT_QPA_PLATFORM=offscreen
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# --- Instalar dependencias básicas y Qt6 runtime mínimo ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git \
    openjdk-17-jdk \
    libgl1 libegl1 libglib2.0-0 libx11-6 libxext6 libxrender1 libxcb1 libxkbcommon-x11-0 libdbus-1-3 \
    libssl-dev zlib1g-dev libglu1-mesa-dev \
    python3-pyqt6 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Actualizar pip, setuptools y wheel ---
RUN python3 -m pip install --upgrade pip setuptools wheel

# --- Instalar Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 -

# --- Crear directorio de trabajo ---
WORKDIR /app

# --- Copiar el proyecto ---
COPY . /app/ParetoInvest

# --- Entrar en la carpeta del proyecto ---
WORKDIR /app/ParetoInvest

# --- Configurar Poetry para virtualenv en proyecto ---
RUN poetry config virtualenvs.in-project true

# --- Instalar dependencias sin PyQt6 (ya está en el sistema) ---
RUN poetry install --no-interaction --no-root

# --- Añadir la raíz al PYTHONPATH para imports relativos ---
ENV PYTHONPATH=/app

# --- Comando por defecto (puedes testear con --help) ---
CMD ["poetry", "run", "python", "ParetoInvest/main.py", "--help"]
