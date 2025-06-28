@echo off
setlocal enabledelayedexpansion

REM === Default config values ===
set "ANACONDA_ROOT=C:\Path\To\Anaconda3"
set "ENV_NAME=ParetoInvest"
set "SCRIPT_NAME=main.py"

REM === Try to load personal config if exists ===
if exist "config\personal_config.json" (
    for /f "tokens=1,* delims=:" %%A in ('findstr /r /c:"\"ANACONDA_ROOT\"" config\personal_config.json') do set "ANACONDA_ROOT=%%~B"
    for /f "tokens=1,* delims=:" %%A in ('findstr /r /c:"\"ENV_NAME\"" config\personal_config.json') do set "ENV_NAME=%%~B"
    for /f "tokens=1,* delims=:" %%A in ('findstr /r /c:"\"SCRIPT_NAME\"" config\personal_config.json') do set "SCRIPT_NAME=%%~B"
) else (
    echo Warning -- personal_config.json not found, using default config.json values.
    if exist "config\config.json" (
        for /f "tokens=1,* delims=:" %%A in ('findstr /r /c:"\"ANACONDA_ROOT\"" config\config.json') do set "ANACONDA_ROOT=%%~B"
        for /f "tokens=1,* delims=:" %%A in ('findstr /r /c:"\"ENV_NAME\"" config\config.json') do set "ENV_NAME=%%~B"
        for /f "tokens=1,* delims=:" %%A in ('findstr /r /c:"\"SCRIPT_NAME\"" config\config.json') do set "SCRIPT_NAME=%%~B"
    )   
)

REM === Clean up values (quotes, commas, spaces) ===
for %%V in (ANACONDA_ROOT ENV_NAME SCRIPT_NAME) do (
    set "val=!%%V!"
    set "val=!val:"=!"
    set "val=!val:,=!"
    set "val=!val: =!"
    set "%%V=!val!"
)

REM === Debug info ===
echo -- CURRENT CONFIGURATION
echo -- Anaconda root     : %ANACONDA_ROOT%
echo -- Conda environment  : %ENV_NAME%
echo -- Script to run      : %SCRIPT_NAME%
echo.

REM === Activate environment ===
echo > Calling: "%ANACONDA_ROOT%\Scripts\activate.bat"
call "%ANACONDA_ROOT%\Scripts\activate.bat"
if errorlevel 1 (
    echo X ERROR activating Anaconda script.
    goto :EOF
)
echo OK activate.bat activated successfully

echo > Activating Conda environment: %ENV_NAME%
call "%ANACONDA_ROOT%\condabin\conda.bat" activate %ENV_NAME%
if errorlevel 1 (
    echo X ERROR activating Conda environment: %ENV_NAME%
    goto :EOF
)
echo OK Conda environment activated: %ENV_NAME%

REM === Change to current directory ===
echo > Changing to script directory: %~dp0
cd /d "%~dp0"

REM === Run script ===
echo > Running script: %SCRIPT_NAME%
python "%SCRIPT_NAME%"
if errorlevel 1 (
    echo X ERROR running %SCRIPT_NAME%
    goto :EOF
)
echo OK Script executed successfully: %SCRIPT_NAME%

pause
