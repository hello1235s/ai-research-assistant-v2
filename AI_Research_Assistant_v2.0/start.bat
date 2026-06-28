@echo off

:: Suppress Python warnings globally (fixes NumPy MINGW-W64 noise on Python 3.13)
set PYTHONWARNINGS=ignore

echo ============================================
echo  AI Research Assistant v2.0
echo ============================================
echo.

cd /d "%~dp0"

echo [INFO] Current directory: %cd%
echo.

:: Check default python version
python -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)" 2>nul
if %errorlevel% equ 0 (
    echo [OK] Python 3.10+ found
    python "%~dp0start_helper.py" run
    goto :end
)

echo [INFO] Default python too old or not found, trying other paths...
echo.

:: Try py -3.12
py -3.12 -V 2>nul
if %errorlevel% equ 0 (
    echo [OK] Found py -3.12
    py -3.12 "%~dp0start_helper.py" run
    goto :end
)

:: Try py -3.11
py -3.11 -V 2>nul
if %errorlevel% equ 0 (
    echo [OK] Found py -3.11
    py -3.11 "%~dp0start_helper.py" run
    goto :end
)

:: Try py -3.10
py -3.10 -V 2>nul
if %errorlevel% equ 0 (
    echo [OK] Found py -3.10
    py -3.10 "%~dp0start_helper.py" run
    goto :end
)

:: Try Daimon Python paths
set "PY=%USERPROFILE%\AppData\Roaming\kimi-desktop\daimon-bundle\runtime\python\cpython-3.12\python.exe"
if exist "%PY%" (
    echo [OK] Found Daimon Python 3.12
    "%PY%" "%~dp0start_helper.py" run
    goto :end
)

set "PY=%USERPROFILE%\AppData\Roaming\kimi-desktop\daimon-bundle\runtime\python\cpython-3.11\python.exe"
if exist "%PY%" (
    echo [OK] Found Daimon Python 3.11
    "%PY%" "%~dp0start_helper.py" run
    goto :end
)

set "PY=%USERPROFILE%\AppData\Roaming\kimi-desktop\daimon-bundle\runtime\python\cpython-3.10\python.exe"
if exist "%PY%" (
    echo [OK] Found Daimon Python 3.10
    "%PY%" "%~dp0start_helper.py" run
    goto :end
)

:: Try standard install paths
for %%P in (
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    "%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python311\python.exe"
    "C:\Program Files\Python310\python.exe"
) do (
    if exist %%P (
        echo [OK] Found Python at %%P
        %%P "%~dp0start_helper.py" run
        goto :end
    )
)

:: Not found
echo.
echo ============================================
echo  ERROR: Python 3.10+ not found!
echo ============================================
echo.
echo  This project requires Python 3.10 or later.
echo.
echo  Please install Python from:
echo  https://www.python.org/downloads/
echo.
echo  During installation, CHECK:
echo  [x] Add Python to PATH
echo  [x] Install pip
echo.
echo  Then run: pip install -r requirements.txt
echo.
pause
exit /b 1

:end
echo.
echo ============================================
echo  Application stopped.
echo ============================================
echo.
pause
