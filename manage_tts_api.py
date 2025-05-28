import subprocess
import sys
import os
import platform
import logging
import socket # Para verificar a porta

# --- Configurações ---
ENV_NAME = "tts_env"
PYTHON_VERSION = "3.10"
# CUDA_VERSION para PyTorch. Use 'cu121' para CUDA 12.1, que é retrocompatível com CUDA 12.9
# Verifique sempre https://pytorch.org/get-started/locally/ para a versão mais recente
PYTORCH_CUDA_VERSION = "cu121" 
# Nome do arquivo da sua aplicação FastAPI
FASTAPI_APP_FILE = "fastapi_app.py"

# Configurações padrão para host e porta (podem ser alteradas pelo menu)
API_HOST = "0.0.0.0"
API_PORT = 5001
# --- Fim das Configurações ---

# Configura o logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_command(command, check_success=True, shell=False):
    """Executa um comando no shell e exibe a saída."""
    logger.info(f"Executando comando: {' '.join(command) if isinstance(command, list) else command}")
    try:
        process = subprocess.run(command, check=check_success, shell=shell, capture_output=True, text=True)
        logger.info(process.stdout)
        if process.stderr:
            logger.warning(process.stderr)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao executar comando: {' '.join(command) if isinstance(command, list) else command}")
        logger.error(f"Detalhes do erro: {e}")
        logger.error(f"Saída STDERR: {e.stderr}")
        return False
    except FileNotFoundError:
        logger.error(f"Comando '{command[0] if isinstance(command, list) else command.split()[0]}' não encontrado. Certifique-se de que está no PATH.")
        return False

def check_conda():
    """Verifica se o Conda está instalado."""
    try:
        subprocess.run(["conda", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Conda não encontrado. Por favor, instale o Anaconda ou Miniconda.")
        return False

def get_conda_env_path(env_name):
    """Obtém o caminho completo para o executável Python de um ambiente Conda."""
    try:
        result = subprocess.run(["conda", "run", "-n", env_name, "python", "-c", "import sys; print(sys.executable)"],
                                check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def is_port_free(host, port):
    """Verifica se uma porta está livre."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind((host, port))
        return True
    except socket.error:
        return False
    finally:
        sock.close()

def install_environment(reinstall=False):
    """Instala ou reinstala o ambiente Conda e as dependências."""
    if not check_conda():
        return

    if reinstall:
        logger.info(f"Removendo ambiente Conda existente: {ENV_NAME}")
        run_command(["conda", "env", "remove", "-n", ENV_NAME, "-y"], check_success=False)

    logger.info(f"Criando ambiente Conda '{ENV_NAME}' com Python {PYTHON_VERSION}...")
    if not run_command(["conda", "create", "-n", ENV_NAME, f"python={PYTHON_VERSION}", "-y"]):
        logger.error("Falha ao criar o ambiente Conda.")
        return

    logger.info(f"Ativando ambiente: {ENV_NAME}")
    
    logger.info(f"Instalando PyTorch com suporte a CUDA {PYTORCH_CUDA_VERSION}...")
    pytorch_install_cmd = [
        "pip", "install", "torch", "torchvision", "torchaudio", 
        "--index-url", f"https://download.pytorch.org/whl/{PYTORCH_CUDA_VERSION}"
    ]
    if not run_command(["conda", "run", "-n", ENV_NAME] + pytorch_install_cmd):
        logger.error("Falha ao instalar PyTorch. Verifique sua versão do CUDA Toolkit e a compatibilidade do PyTorch.")
        return

    logger.info("Verificando instalação do CUDA no PyTorch...")
    python_exec_path = get_conda_env_path(ENV_NAME)
    if python_exec_path:
        cuda_check_cmd = [
            python_exec_path, "-c", 
            "import torch; print(f'CUDA disponível: {torch.cuda.is_available()}'); "
            "if torch.cuda.is_available(): print(f'Nome da GPU: {torch.cuda.get_device_name(0)}') "
            "else: print('GPU não detectada ou CUDA não disponível.')"
        ]
        run_command(cuda_check_cmd)
    else:
        logger.error("Não foi possível obter o caminho do Python no ambiente Conda para verificar o CUDA.")


    logger.info("Instalando TTS, transformers, FastAPI e Uvicorn...")
    other_deps_cmd = ["pip", "install", "TTS", "transformers", "fastapi", "uvicorn", "accelerate"]
    if not run_command(["conda", "run", "-n", ENV_NAME] + other_deps_cmd):
        logger.error("Falha ao instalar outras dependências.")
        return

    logger.info("Instalação/Reinstalação concluída com sucesso!")
    logger.info(f"Agora você pode iniciar a API usando a opção 'Iniciar API' do script ou manualmente com: conda activate {ENV_NAME} && uvicorn {FASTAPI_APP_FILE.replace('.py', '')}:app --reload --host {API_HOST} --port {API_PORT}")


def start_api():
    """Inicia a API FastAPI."""
    global API_HOST, API_PORT
    logger.info("Iniciando a API FastAPI...")
    api_script_path = os.path.join(os.getcwd(), FASTAPI_APP_FILE)
    
    if not os.path.exists(api_script_path):
        logger.error(f"Arquivo '{FASTAPI_APP_FILE}' não encontrado em: {os.getcwd()}")
        logger.error(f"Certifique-se de que o script 'manage_tts_api.py' está na mesma pasta que '{FASTAPI_APP_FILE}'.")
        return

    if not is_port_free(API_HOST, API_PORT):
        logger.error(f"A porta {API_PORT} no host {API_HOST} já está em uso. Por favor, libere a porta ou configure uma nova.")
        return

    logger.info(f"API será iniciada em http://{API_HOST}:{API_PORT}")
    logger.info("Pressione CTRL+C para parar a API.")
    try:
        # Comando para iniciar o Uvicorn com o aplicativo FastAPI
        uvicorn_command = f"uvicorn {FASTAPI_APP_FILE.replace('.py', '')}:app --reload --host {API_HOST} --port {API_PORT}"
        
        if platform.system() == "Windows":
            p = subprocess.Popen(f"conda activate {ENV_NAME} && {uvicorn_command}", shell=True)
        else: # Linux/macOS
            p = subprocess.Popen(f"conda run -n {ENV_NAME} {uvicorn_command}", shell=True)
        
        p.wait()
    except KeyboardInterrupt:
        logger.info("API interrompida pelo usuário.")
    except Exception as e:
        logger.error(f"Ocorreu um erro ao iniciar a API: {e}")

def configure_host_port():
    """Permite ao usuário configurar o host e a porta da API."""
    global API_HOST, API_PORT
    logger.info("\n--- Configurar Host e Porta da API ---")
    new_host = input(f"Host atual: {API_HOST}. Digite o novo host (ex: 127.0.0.1 ou 0.0.0.0) ou Enter para manter: ").strip()
    if new_host:
        API_HOST = new_host
    
    new_port_str = input(f"Porta atual: {API_PORT}. Digite a nova porta (ex: 8000) ou Enter para manter: ").strip()
    if new_port_str:
        try:
            new_port = int(new_port_str)
            if 1024 <= new_port <= 65535: # Portas válidas não-privilegiadas
                API_PORT = new_port
            else:
                logger.warning("Porta inválida. Use um número entre 1024 e 65535.")
        except ValueError:
            logger.warning("Entrada inválida para porta. Por favor, digite um número.")
    
    logger.info(f"Host e Porta configurados para: {API_HOST}:{API_PORT}")

def clear_cache():
    """Limpa o diretório de cache de áudio."""
    cache_dir_path = os.path.join(os.getcwd(), "cached_audio")
    logger.info(f"Tentando limpar o diretório de cache: {cache_dir_path}")
    if os.path.exists(cache_dir_path):
        try:
            for filename in os.listdir(cache_dir_path):
                file_path = os.path.join(cache_dir_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    logger.debug(f"Removido: {file_path}")
            logger.info("Cache de áudio limpo com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao limpar o cache: {e}")
    else:
        logger.info("Diretório de cache não encontrado, nada para limpar.")

def main_menu():
    """Exibe o menu principal e gerencia as opções."""
    while True:
        logger.info("\n--- Menu de Gerenciamento da API TTS (FastAPI) ---")
        logger.info("1. Instalar ambiente e dependências (primeira vez)")
        logger.info("2. Reinstalar tudo (ambiente e dependências - para resolver erros)")
        logger.info("3. Iniciar a API FastAPI")
        logger.info("4. Configurar Host e Porta da API")
        logger.info("5. Limpar Cache de Áudio")
        logger.info("6. Sair")

        choice = input("Escolha uma opção: ")

        if choice == '1':
            install_environment(reinstall=False)
        elif choice == '2':
            install_environment(reinstall=True)
        elif choice == '3':
            start_api()
        elif choice == '4':
            configure_host_port()
        elif choice == '5':
            clear_cache()
        elif choice == '6':
            logger.info("Saindo do script. Até mais!")
            sys.exit(0)
        else:
            logger.warning("Opção inválida. Por favor, tente novamente.")

if __name__ == "__main__":
    logger.info("Bem-vindo ao Gerenciador da API TTS.")
    main_menu()
