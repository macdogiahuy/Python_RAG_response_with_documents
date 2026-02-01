@echo off
chcp 65001 > nul
cd /d "%~dp0"

echo ===============================================================================
echo                KHOI DONG HE THONG AI...
echo ===============================================================================

:: Check Ollama
tasklist /FI "IMAGENAME eq ollama_app.exe" 2>NUL | find /I /N "ollama_app.exe">NUL
if "%ERRORLEVEL%"=="0" (
    echo [OK] Ollama dang chay.
) else (
    echo [!] Ollama chua chay. Dang khoi dong Ollama...
    start ollama serve
    timeout /t 5 >nul
)

echo Dang kich hoat moi truong...
call venv\Scripts\activate

echo Dang mo ung dung...
echo Vui long cho trong giay lat, trinh duyet se tu dong mo.
streamlit run app/app.py

pause
