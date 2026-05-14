@echo off
setlocal EnableDelayedExpansion

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=python"
set "SCRIPT_PATH=%SCRIPT_DIR%pdf_to_static.py"

set "INPUT_DIR=%SCRIPT_DIR%test-pdfs"
set "OUTPUT_DIR=%SCRIPT_DIR%presentation"
set "DPI=144"
set "QUALITY=80"
set "SITE_TITLE=PDF Presentations"

if not "%~1"=="" (
  set "INPUT_DIR=%~1"
)

if not "%~2"=="" (
  set "SITE_TITLE=%~2"
) else (
  set /p "SITE_TITLE_INPUT=Site title [PDF Presentations]: "
  if not "!SITE_TITLE_INPUT!"=="" (
    set "SITE_TITLE=!SITE_TITLE_INPUT!"
  )
)

if not "%PDF_TO_HTML_PYTHON%"=="" (
  set "PYTHON_EXE=%PDF_TO_HTML_PYTHON%"
)

set "PYTHON_USER_SITE=%APPDATA%\Python\Python313\site-packages"
set "PYTHONPATH=%PYTHON_USER_SITE%"

echo Running PDF to Reveal.js presentation conversion...
echo Python: %PYTHON_EXE%
echo Input:  %INPUT_DIR%
echo Output: %OUTPUT_DIR%
echo Title:  %SITE_TITLE%
echo.

"%PYTHON_EXE%" -c "import pypdfium2, PIL" >nul 2>nul
if errorlevel 1 (
  echo Missing Python dependencies.
  echo Please run:
  echo   python -m pip install -r "%SCRIPT_DIR%requirements.txt"
  exit /b 1
)

"%PYTHON_EXE%" "%SCRIPT_PATH%" --input-dir "%INPUT_DIR%" --output-dir "%OUTPUT_DIR%" --dpi %DPI% --quality %QUALITY% --site-title "%SITE_TITLE%"

if errorlevel 1 (
  echo.
  echo Conversion failed.
  exit /b 1
)

echo.
echo Conversion completed.
echo Output index: %OUTPUT_DIR%\index.html
echo.
echo Open the index file in Chrome, then click a document link to view its slides.
pause
exit /b 0
