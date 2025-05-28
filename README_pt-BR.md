
# 🔊 Projeto de Síntese de Voz com Coqui TTS e FastAPI

Este projeto oferece uma **API REST moderna** e uma **interface web** para sintetizar voz a partir de texto, utilizando o modelo **XTTS-v2 da Coqui TTS**. A API é construída com **FastAPI** para alta performance e inclui um sistema de **cache inteligente** para otimizar requisições repetidas.

A interface web foi desenvolvida com **HTML + Tailwind CSS + JavaScript**, proporcionando uma experiência de usuário elegante, responsiva e com suporte a **Dark/Light Mode** e notificações.

---

## 📂 Estrutura do Projeto

```
seu_projeto/
├── fastapi_app.py           # Código da API FastAPI
├── index.html               # Interface web
├── manage_tts_api.py        # Script para gerenciar ambiente e API
├── start.bat                # Script para iniciar no Windows
├── speaker.wav              # Arquivo de voz de referência (clonagem)
├── Dockerfile               # Dockerfile com suporte a GPU (CUDA)
├── Dockerfile.cpu           # Dockerfile para CPU (alternativo)
├── docker-compose.yml       # Orquestração opcional com Docker Compose
└── cached_audio/            # Áudios em cache (gerado automaticamente)
```

---

## 💻 Requisitos

- **Sistema Operacional:** Windows, Linux ou macOS
- **Conda:** Anaconda ou Miniconda (para execução local)
- **GPU NVIDIA (Recomendado):** Para aceleração via CUDA no Docker ou local
- **NVIDIA Container Toolkit:** Necessário para Docker com GPU ([instalar aqui](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html))
- **CUDA Toolkit:** Suporte CUDA 12.x para execução local com GPU
- **Conexão com a internet:** Para baixar modelos na primeira vez

---

## 🚀 Instalação Manual (Sem Docker)

1. Execute:

```
start.bat
```

ou manualmente:

```
python manage_tts_api.py
```

2. No menu, selecione:

```
1. Instalar ambiente e dependências
```

Aguarde a instalação.

---

## 🐳 Execução com Docker (Recomendado)

### 🔥 GPU (Prioritário)

**Build manual:**
```bash
docker build -t tts-api .
docker run --gpus all -p 5001:5001 -v ${PWD}/cached_audio:/app/cached_audio tts-api
```

### 🖥️ CPU (Alternativo)

**Build manual:**
```bash
docker build -t tts-api-cpu -f Dockerfile.cpu .
docker run -p 5001:5001 -v ${PWD}/cached_audio:/app/cached_audio tts-api-cpu
```

### ⚙️ Usando Docker Compose (recomendado)

```bash
docker-compose up --build
```

✔️ O `docker-compose.yml` já está configurado para usar GPU por padrão. Se quiser rodar na CPU, edite e remova:

```yaml
deploy:
  resources:
    reservations:
      devices:
        - capabilities: [gpu]
```

---

## 🌐 Usando a Interface Web

Após iniciar a API, acesse:

```
http://localhost:5001
```

Funcionalidades:
- Campo de texto para sintetizar voz
- Seletor de idioma
- Player de áudio customizado
- Download do áudio gerado
- Dark/Light Mode
- Toast notifications

---

## 📚 Documentação da API (Swagger)

Acesse:

```
http://localhost:5001/docs
```

### 🔗 Endpoints:

| Método | Endpoint         | Descrição                                     |
|--------|-------------------|-----------------------------------------------|
| POST   | `/synthesize`     | Gera áudio e retorna JSON com o caminho.      |
| POST   | `/api/audio`      | Gera áudio e retorna diretamente o .wav.      |
| GET    | `/`               | Retorna a interface web (index.html).         |
| GET    | `/{path:path}`    | Servir arquivos (cached_audio, speaker.wav).  |
| GET    | `/health`         | Verifica a saúde da API e do modelo.          |

### 🔊 Corpo da requisição (POST):

```json
{
  "text": "Olá mundo",
  "language": "pt"
}
```

### 🔥 Resposta exemplo:

```json
{
  "message": "Áudio gerado com sucesso!",
  "output_file": "cached_audio/89f7f526811668c14c0047a600799b26.wav"
}
```

---

## 📦 Cache de Áudio

Os arquivos gerados são armazenados no diretório `cached_audio/`.

- Nomeados por um hash único do texto + idioma.
- Exemplo:

```
cached_audio/89f7f526811668c14c0047a600799b26.wav
```

Se você enviar o mesmo texto e idioma novamente, o áudio é recuperado instantaneamente do cache.

---

## 🌍 Idiomas Suportados

- 🇺🇸 English (en)
- 🇪🇸 Spanish (es)
- 🇫🇷 French (fr)
- 🇩🇪 German (de)
- 🇮🇹 Italian (it)
- 🇵🇹 Portuguese (pt)
- 🇵🇱 Polish (pl)
- 🇹🇷 Turkish (tr)
- 🇷🇺 Russian (ru)
- 🇳🇱 Dutch (nl)
- 🇨🇿 Czech (cs)
- 🇸🇦 Arabic (ar)
- 🇨🇳 Chinese Simplified (zh-cn)
- 🇯🇵 Japanese (ja)
- 🇭🇺 Hungarian (hu)
- 🇰🇷 Korean (ko)
- 🇮🇳 Hindi (hi)

---

## 🛠️ Solução de Problemas

| Erro                                                | Solução                                               |
|------------------------------------------------------|-------------------------------------------------------|
| Conda não encontrado                                | Instale Miniconda ou Anaconda.                        |
| `speaker.wav não encontrado`                        | Coloque o arquivo `speaker.wav` na mesma pasta.       |
| Porta já em uso                                     | Use a opção 4 no menu para mudar a porta.             |
| TypeError: TTS() got an unexpected keyword 'device' | Corrigido nesta versão (usa .to(device) corretamente).|

---

## 🚀 Otimizações Futuras

- [ ] Implementar **Rate Limiting** real.
- [ ] Transformar em **PWA**.
- [ ] Adicionar autenticação por token (JWT ou API Key).
- [ ] Dockerização com cache distribuído (Redis).
- [ ] Deploy na nuvem (Render, Railway, AWS).

---

## 💙 Créditos

- Baseado no modelo **XTTS-v2 da Coqui TTS**.
- Interface web feita com **HTML + Tailwind CSS + JavaScript**.
- Backend desenvolvido com **FastAPI + Python**.

---

## 📜 Licença

Este projeto está licenciado sob a **Licença MIT**. Consulte o arquivo `LICENSE` para mais detalhes.

---

## 🏆 Status

**Pronto para produção local, em container (Docker com GPU/CPU) e escalável para deploy em nuvem.**
