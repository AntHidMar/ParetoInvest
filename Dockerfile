FROM openjdk:17-jdk-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV QT_QPA_PLATFORM=offscreen
ENV PYTHONUNBUFFERED=1

# --- Instalar Python, pip, curl, build-essential y librerías necesarias para PyQt6 ---
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-dev build-essential curl \
    libgl1 libglib2.0-0 libx11-6 libx11-dev libxext6 libxext-dev libxrender1 libxrender-dev \
    libxcb1 libxcb1-dev libxkbcommon-x11-0 libxkbcommon-x11-dev libdbus-1-3 \
    libglu1-mesa-dev libssl-dev zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- Actualizar pip y preinstalar PyQt6 ---
RUN python3 -m pip install --upgrade pip setuptools wheel
RUN python3 -m pip install PyQt6==6.10.0

# --- Instalar Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY . /app/ParetoInvest
WORKDIR /app/ParetoInvest

# --- Opcional: inspección del entorno ---
RUN poetry env info && poetry check

# --- Instalar dependencias con Poetry ---
RUN poetry install --no-interaction --no-ansi -vvv

ENV PYTHONPATH=/app

CMD ["poetry", "run", "python", "ParetoInvest/main.py"]
