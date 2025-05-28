
# Dockerfile para GPU (CUDA como padrão)

FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# Variáveis de ambiente
ENV DEBIAN_FRONTEND=noninteractive
ENV CACHE_DIR=/app/cached_audio

# Instala dependências do sistema
RUN apt-get update && apt-get install -y     python3 python3-pip python3-venv ffmpeg     && rm -rf /var/lib/apt/lists/*

# Cria diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . /app

# Instala dependências Python
RUN pip3 install --upgrade pip     && pip3 install torch==2.2.0+cu121 --index-url https://download.pytorch.org/whl/cu121     && pip3 install TTS fastapi uvicorn[standard] transformers accelerate

# Cria diretório de cache
RUN mkdir -p $CACHE_DIR

# Expõe a porta
EXPOSE 5001

# Comando para rodar a API
CMD ["uvicorn", "fastapi_app:app", "--host", "0.0.0.0", "--port", "5001"]
