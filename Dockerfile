# --- Imagen base con Java y Python ---
FROM openjdk:17-slim

# --- Variables de entorno ---
ENV DEBIAN_FRONTEND=noninteractive
ENV QT_QPA_PLATFORM=offscreen
ENV PYTHONUNBUFFERED=1

# --- Instalar Python, pip, curl, build-essential y librerías para PyQt6 ---
RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-dev build-essential curl \
    libgl1 libglib2.0-0 libx11-6 libxext6 libxrender1 libxcb1 libxkbcommon-x11-0 libdbus-1-3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# --- Instalar Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 -

# --- Añadir Poetry al PATH ---
ENV PATH="/root/.local/bin:$PATH"

# --- Crear directorio de trabajo ---
WORKDIR /app

# --- Copiar el proyecto completo ---
COPY . /app/ParetoInvest

# --- Entrar en la carpeta del proyecto ---
WORKDIR /app/ParetoInvest

# --- Instalar dependencias con Poetry ---
# Instalamos el entorno completo (paquete + dependencias)
RUN poetry install --no-interaction --no-ansi

# --- Añadir la raíz al PYTHONPATH (para imports relativos) ---
ENV PYTHONPATH=/app

# --- Comando por defecto ---
CMD ["poetry", "run", "python", "ParetoInvest/main.py"]
