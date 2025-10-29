# --- Imagen base con Python 3.11 y JDK 17 (para tu parte Java) ---
FROM ubuntu:24.04

# --- Variables de entorno ---
ENV DEBIAN_FRONTEND=noninteractive
ENV QT_QPA_PLATFORM=offscreen
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"

# --- Instalar dependencias básicas: Python, JDK, build tools, librerías de Qt/GUI ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3-pip python3.11-dev \
    openjdk-17-jdk \
    build-essential curl git \
    libgl1 libegl1 libglib2.0-0 libx11-6 libxext6 libxrender1 libxcb1 libxkbcommon-x11-0 libdbus-1-3 \
    libssl-dev zlib1g-dev libglu1-mesa-dev \
    qt6-base-dev qt6-qmake qt6-base-dev-tools \
    python3-pyqt6 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Actualizar pip, setuptools y wheel ---
RUN python3 -m pip install --upgrade pip setuptools wheel

# --- Instalar Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 -

# --- Crear directorio de trabajo ---
WORKDIR /app

# --- Copiar todo el proyecto ---
COPY . /app/ParetoInvest

# --- Entrar en la carpeta del proyecto ---
WORKDIR /app/ParetoInvest

# --- Configurar Poetry para crear el virtualenv dentro del proyecto ---
RUN poetry config virtualenvs.in-project true

# --- Instalar dependencias de Poetry sin PyQt6 (ya está en el sistema) ---
# --- Si tu pyproject.toml tiene pyqt6-qt6, elimínalo para evitar fallos ---
RUN poetry install --no-interaction --no-root

# --- Añadir la raíz al PYTHONPATH para imports relativos ---
ENV PYTHONPATH=/app

# --- Comando por defecto (puedes testear con --help) ---
CMD ["poetry", "run", "python", "ParetoInvest/main.py", "--help"]
