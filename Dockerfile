FROM ubuntu:22.04

# Set environment variables to avoid interactive prompts
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

# --- Dependencias básicas ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3.11-dev python3-pip \
    openjdk-17-jdk \
    build-essential curl git \
    libgl1 libegl1 libglib2.0-0 libx11-6 libxext6 libxrender1 \
    libxcb1 libxkbcommon-x11-0 libdbus-1-3 \
    libssl-dev zlib1g-dev libglu1-mesa-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Create symbolic links for python3
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

# --- Instalar Poetry ---
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry

WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml poetry.lock* ./

# Install dependencies INCLUDING the root package
RUN poetry install --no-interaction --no-root

# Now copy the rest of the application
COPY . .

# Install the actual package with dependencies
RUN poetry install --no-interaction

CMD ["poetry", "run", "python", "ParetoInvest/main.py", "--help"]