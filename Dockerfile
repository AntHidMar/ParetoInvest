# --- Imagen base con Java y Python ---
FROM openjdk:17-slim

# --- Instalar Python, pip y curl para Poetry ---
RUN apt-get update && apt-get install -y python3 python3-pip curl && rm -rf /var/lib/apt/lists/*

# --- Instalar Poetry ---
RUN curl -sSL https://install.python-poetry.org | python3 -

# --- Añadir Poetry al PATH ---
ENV PATH="/root/.local/bin:$PATH"

# --- Crear directorio de trabajo ---
WORKDIR /app

# --- Copiar proyecto completo ---
COPY . .

# --- Instalar dependencias Python con Poetry ---
RUN poetry install --no-root

# --- Añadir la raíz al PYTHONPATH para que los imports funcionen ---
ENV PYTHONPATH=/app

# --- Comando por defecto: ejecutar main.py ---
CMD ["poetry", "run", "python", "main.py"]
