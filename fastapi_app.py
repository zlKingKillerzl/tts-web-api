import os
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from TTS.api import TTS
import torch
import logging
import hashlib
import asyncio
from pydantic import BaseModel, Field # Importa Field para validação de tamanho

# --- Configurações de Logging ---
logging.basicConfig(level=logging.DEBUG, # Nível de log para DEBUG para ver tudo
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app_logger = logging.getLogger(__name__)
# --- Fim das Configurações de Logging ---

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="API de Síntese de Voz com Coqui TTS",
    description="API para gerar áudio a partir de texto usando o modelo XTTS-v2, com cache em memória, agora em FastAPI.",
    version="1.0.0",
)

# --- Modelo Pydantic para o Corpo da Requisição ---
class SynthesisRequest(BaseModel):
    """
    Define o modelo de dados esperado para as requisições de síntese de voz.
    Isso permite que o FastAPI gere automaticamente a documentação da API.
    Adicionado limite de tamanho para o texto para segurança e performance.
    """
    text: str = Field(..., min_length=1, max_length=1000, description="Texto para ser sintetizado (máx. 1000 caracteres).")
    language: str = Field(..., min_length=2, max_length=5, description="Código do idioma (ex: 'pt', 'en').")

# --- Configuração do Modelo TTS ---
tts = None # O modelo será carregado na inicialização (startup) da aplicação
@app.on_event("startup")
async def load_tts_model():
    """
    Carrega o modelo TTS na inicialização da aplicação FastAPI.
    Este evento é assíncrono.
    """
    global tts
    device = "cuda" if torch.cuda.is_available() else "cpu"
    app_logger.info(f"Dispositivo detectado para TTS: {device.upper()}")

    try:
        app_logger.info("Tentando carregar o modelo TTS (isto pode levar tempo)...")
        
        # CORREÇÃO: Inicializa TTS sem o argumento 'device', e depois usa .to(device)
        # O asyncio.to_thread é usado porque TTS() e .to() são operações síncronas
        tts_instance = await asyncio.to_thread(TTS, "tts_models/multilingual/multi-dataset/xtts_v2")
        tts = tts_instance.to(device) # Move o modelo para o dispositivo detectado
        
        app_logger.info("Modelo TTS carregado com sucesso.")
    except Exception as e:
        app_logger.exception(f"Erro ao carregar o modelo TTS: {e}")
        app_logger.error("Falha crítica ao carregar o modelo TTS. A API não funcionará corretamente.")
        # Em FastAPI, você pode levantar uma exceção para impedir o startup se o modelo for crítico
        # raise RuntimeError("Falha crítica ao carregar o modelo TTS.")

# --- Cache em Memória para Áudios Gerados ---
CACHE_DIR = "cached_audio"
os.makedirs(CACHE_DIR, exist_ok=True) # Cria o diretório de cache se não existir
app_logger.info(f"Diretório de cache de áudio: {os.path.abspath(CACHE_DIR)}")
# --- Fim do Cache ---

# --- Funções Auxiliares para Síntese e Cache ---
async def _process_synthesis(text: str, language: str):
    """
    Função auxiliar para processar a síntese de voz e gerenciar o cache.
    Retorna o caminho completo do arquivo de áudio gerado/cacheado.
    """
    if tts is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="O modelo TTS não foi carregado corretamente.")

    # Gerar uma chave de cache única para o texto e idioma
    cache_key = hashlib.md5(f"{text}-{language}".encode('utf-8')).hexdigest()
    cached_audio_filename = f"{cache_key}.wav"
    cached_audio_filepath = os.path.join(CACHE_DIR, cached_audio_filename)

    # Verificar se o áudio já está em cache
    if os.path.exists(cached_audio_filepath):
        app_logger.info(f"Áudio encontrado no cache para a requisição: {cached_audio_filename}")
        return cached_audio_filepath

    speaker_wav_path = os.path.join(os.getcwd(), "speaker.wav")
    app_logger.debug(f"Caminho do speaker_wav: {speaker_wav_path}")

    if not os.path.exists(speaker_wav_path):
        app_logger.error(f"Arquivo speaker.wav não encontrado em: {speaker_wav_path}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Arquivo speaker.wav não encontrado em: {speaker_wav_path}. Por favor, coloque o arquivo na mesma pasta da API.")

    try:
        app_logger.info(f"Iniciando síntese para o idioma '{language}' com texto de {len(text)} caracteres.")
        await asyncio.to_thread(
            tts.tts_to_file,
            text=text,
            file_path=cached_audio_filepath, # Salva diretamente no diretório de cache
            speaker_wav=speaker_wav_path,
            language=language
        )
        app_logger.info(f"Áudio gerado com sucesso e salvo em cache: {cached_audio_filename}")
        app_logger.debug(f"Verificando arquivo salvo: {os.path.exists(cached_audio_filepath)}")
        return cached_audio_filepath
    except Exception as e:
        app_logger.exception("Erro durante a geração do áudio:")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Erro ao gerar áudio: {e}")

# --- Rotas da API e Servidor de Arquivos ---

# Endpoint de Health Check
@app.get("/health", summary="Verifica a saúde da API")
async def health_check():
    """
    Retorna o status da API e do carregamento do modelo TTS.
    """
    if tts is None:
        return {"status": "unhealthy", "model_loaded": False, "message": "Modelo TTS não carregado."}
    return {"status": "healthy", "model_loaded": True, "message": "API e modelo TTS funcionando."}

# Rota para servir a interface web (index.html)
@app.get("/", summary="Servir a interface web HTML")
async def read_root():
    app_logger.debug("Requisição recebida para a raiz. Servindo index.html")
    return FileResponse("index.html", media_type="text/html")

# Rota para servir arquivos estáticos gerais (incluindo favicon.ico e arquivos em cache)
# Usamos /{path:path} para capturar o caminho completo, incluindo subdiretórios
@app.get("/{path_in_request:path}", summary="Servir arquivos estáticos (áudios gerados ou em cache)")
async def serve_static_files(path_in_request: str):
    app_logger.debug(f"Requisição recebida para arquivo estático: {path_in_request}")
    
    # Prioriza arquivos na raiz (como speaker.wav, favicon.ico)
    if path_in_request == 'speaker.wav':
        file_path = os.path.join(os.getcwd(), path_in_request)
        if os.path.exists(file_path):
            app_logger.debug(f"Servindo speaker.wav de: {file_path}")
            return FileResponse(file_path)
        else:
            app_logger.warning(f"speaker.wav solicitado, mas não encontrado em: {file_path}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="speaker.wav não encontrado.")
    elif path_in_request == 'favicon.ico':
        file_path = os.path.join(os.getcwd(), path_in_request)
        if os.path.exists(file_path):
            app_logger.debug(f"Servindo favicon.ico de: {file_path}")
            return FileResponse(file_path)
        else:
            app_logger.warning("favicon.ico solicitado, mas não encontrado.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="favicon.ico não encontrado.")
    
    # Tenta servir arquivos do diretório de cache
    # Ex: se path_in_request for "cached_audio/abc.wav"
    elif path_in_request.startswith(f"{CACHE_DIR}/"):
        # Extrai apenas o nome do arquivo do caminho, para segurança
        file_name_in_cache = os.path.basename(path_in_request)
        file_path_full = os.path.join(CACHE_DIR, file_name_in_cache)
        
        app_logger.debug(f"Tentando servir arquivo de cache: {file_path_full}")
        if os.path.exists(file_path_full):
            app_logger.debug(f"Servindo arquivo em cache: {file_path_full}")
            return FileResponse(file_path_full, media_type="audio/wav") # Garante o media_type correto
        else:
            app_logger.error(f"Arquivo em cache não encontrado no disco: {file_path_full}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo de áudio em cache não encontrado.")

    # Se não for nenhum dos acima, é um arquivo não permitido ou não encontrado
    app_logger.warning(f"Tentativa de acesso a arquivo não permitido ou não encontrado: {path_in_request}")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arquivo não encontrado ou não permitido.")


@app.post("/synthesize", summary="Sintetizar áudio e retornar JSON com o caminho do arquivo")
# Placeholder para Rate Limit: Para implementar, você precisaria de uma biblioteca como fastapi-limiter
# Ex: @limiter.limit("5/minute")
async def synthesize_speech_json(request: SynthesisRequest):
    app_logger.info("Requisição de síntese de voz (JSON) recebida.")
    
    # Acessa os dados diretamente do objeto Pydantic
    language = request.language
    text = request.text

    audio_filepath = await _process_synthesis(text, language)
    
    # Retorna o caminho relativo do arquivo para o frontend
    relative_path = os.path.join(CACHE_DIR, os.path.basename(audio_filepath))
    return JSONResponse({"message": "Áudio gerado com sucesso!", "output_file": relative_path})


@app.post("/api/audio", summary="Sintetizar áudio e retornar o arquivo WAV diretamente")
# Placeholder para Rate Limit
# Ex: @limiter.limit("5/minute")
async def synthesize_direct_audio(request: SynthesisRequest):
    app_logger.info("Requisição de síntese de voz (Áudio Direto) recebida.")
    
    # Acessa os dados diretamente do objeto Pydantic
    language = request.language
    text = request.text

    audio_filepath = await _process_synthesis(text, language)
    
    # Retorna o arquivo WAV diretamente
    app_logger.info(f"Retornando arquivo WAV diretamente: {audio_filepath}")
    return FileResponse(audio_filepath, media_type="audio/wav", filename=os.path.basename(audio_filepath))


# --- Execução da API ---
# Para rodar esta API:
# 1. Certifique-se de que o ambiente 'tts_env' está ativado.
# 2. Instale o FastAPI e o Uvicorn:
#    pip install fastapi uvicorn
# 3. Salve o código acima como 'fastapi_app.py'
# 4. Execute o servidor Uvicorn:
#    uvicorn fastapi_app:app --reload --host 0.0.0.0 --port 5001
#    (Para produção, considere usar workers: uvicorn fastapi_app:app --host 0.0.0.0 --port 5001 --workers 2)
