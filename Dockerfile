FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    QT_QPA_PLATFORM=offscreen \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# --- Dependencias básicas del sistema y soporte Qt ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3.11-dev python3-pip \
    build-essential curl git \
    libgl1 libegl1 libglib2.0-0 libx11-6 libxext6 libxrender1 \
    libxcb1 libxkbcommon-x11-0 libdbus-1-3 \
    libssl-dev zlib1g-dev libglu1-mesa-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Crear symlinks para python3 ---
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

# --- Instalar Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# --- Copiar archivos de dependencias primero (para caching) ---
COPY pyproject.toml poetry.lock* ./

# --- Instalar dependencias de Python ---
RUN poetry install --no-interaction --no-root

# --- Copiar todo el código ---
COPY . .

# --- Comando por defecto ---
CMD ["poetry", "run", "python", "ParetoInvest/main.py", "--help"]
