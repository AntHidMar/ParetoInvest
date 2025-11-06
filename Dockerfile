# --- Base image ---
FROM ubuntu:22.04

# --- Environment variables ---
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    QT_QPA_PLATFORM=offscreen \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_PATH="/opt/.venvs" \
    POETRY_NO_INTERACTION=1

# --- System dependencies and Qt support ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3.11-dev python3-pip \
    build-essential curl git \
    fontconfig libfreetype6 libxft2 \
    libgl1 libegl1 libglib2.0-0 libx11-6 libxext6 libxrender1 \
    libxcb1 libxkbcommon-x11-0 libdbus-1-3 \
    libssl-dev zlib1g-dev libglu1-mesa-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# --- Symlink python3 for consistency ---
RUN ln -sf /usr/bin/python3.11 /usr/bin/python3 && \
    ln -sf /usr/bin/python3.11 /usr/bin/python

# --- Install Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

# --- Install PyQt6 globally (optional but ensures compatibility) ---
RUN pip install pyqt6==6.10.0

# --- Set working directory ---
WORKDIR /app

# --- Copy dependency files first to leverage Docker caching ---
COPY pyproject.toml poetry.lock* ./

# --- Install Python dependencies via Poetry (without installing the local package) ---
RUN poetry install --no-root --no-interaction

# --- Copy the rest of the application code ---
COPY . .

# --- Default command to run the application or tests ---
CMD ["poetry", "run", "python", "ParetoInvest/main.py"]
