FROM ubuntu:22.04

# --- Dependencias básicas ---
RUN apt-get update && apt-get install -y \
    python3.11 python3.11-venv python3-pip \
    openjdk-17-jdk \
    build-essential curl git \
    libgl1 libegl1 libglib2.0-0 libx11-6 libxext6 libxrender1 \
    libxcb1 libxkbcommon-x11-0 libdbus-1-3 \
    libssl-dev zlib1g-dev libglu1-mesa-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Instalar Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app
COPY . /app

RUN poetry config virtualenvs.in-project true
RUN poetry install --no-interaction --no-root

CMD ["poetry", "run", "python", "ParetoInvest/main.py", "--help"]
