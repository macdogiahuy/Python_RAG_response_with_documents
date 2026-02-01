@echo off
chcp 65001 > nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ===============================================================================
echo                CAI DAT TU DONG - HE THONG AI TRA CUU TAI LIEU
echo ===============================================================================
echo.

:: 1. Check Python
echo [1/5] Kiem tra Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    ! Python chua duoc cai dat. Dang thu cai dat tu dong bang Winget...
    winget install -e --id Python.Python.3.11
    if %errorlevel% neq 0 (
        echo    [LOI] Khong the cai dat Python tu dong.
        echo    Vui long tai va cai dat Python thu cong tai: https://www.python.org/downloads/
        pause
        exit /b
    )
    echo    ! Da cai dat Python. Vui long khoi dong lai file nay.
    pause
    exit /b
) else (
    echo    OK (Python da san sang)
)

:: 2. Check Ollama
echo [2/5] Kiem tra Ollama...
ollama --version >nul 2>&1
if %errorlevel% neq 0 (
    echo    ! Ollama chua duoc cai dat.
    echo    Dang mo trinh duyet de tai Ollama. Vui long cai dat va chay file nay lai.
    start https://ollama.com/download
    pause
    exit /b
) else (
    echo    OK (Ollama da san sang)
)

:: 3. Create Virtual Environment
echo [3/5] Tao moi truong ao (Virtual Environment)...
if not exist "venv" (
    python -m venv venv
    echo    Da tao moi truong ao 'venv'.
) else (
    echo    Moi truong ao da ton tai.
)

:: 4. Install Dependencies
echo [4/5] Cai dat thu vien can thiet...
call venv\Scripts\activate
pip install -r app\requirements.txt
if %errorlevel% neq 0 (
    echo    [LOI] Co loi khi cai dat thu vien.
    pause
    exit /b
)

:: 5. Pull Ollama Models
echo [5/5] Tai mo hinh AI ve may (Lan dau se mat thoi gian)...
echo    - Tai mo hinh nhung (Embedding): nomic-embed-text...
ollama pull nomic-embed-text
echo    - Tai mo hinh ngon ngu (LLM): llama3.2...
ollama pull llama3.2:1b

echo.
echo ===============================================================================
echo                CAI DAT HOAN TAT!
echo ===============================================================================
echo Ban co the bat dau su dung bang file 'run_app.bat'.
pause
