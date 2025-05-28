@echo off
REM Script para ativar o ambiente Conda e rodar manage_tts_api.py automaticamente

REM Nome do ambiente Conda
set CONDA_ENV_NAME=tts_env

REM Obtém o caminho base do Conda
FOR /F "delims=" %%i IN ('conda info --base') DO SET CONDA_BASE=%%i

REM Ativa o Conda
CALL "%CONDA_BASE%\Scripts\activate.bat"

REM Ativa o ambiente desejado
CALL conda activate %CONDA_ENV_NAME%

REM Executa o script Python
python manage_tts_api.py

REM Mantém a janela aberta após terminar
pause
