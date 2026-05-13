# [SD06] Use esta imagem base específica para garantir compatibilidade com apt-get e OpenCV
FROM python:3.9-slim-bookworm

# Correção do formato ENV (use '=' conforme sugerido pelo aviso do Docker)
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# [SD06] Agora o apt-get funcionará corretamente nesta base Debian
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código
COPY . .