@echo off
setlocal

set ROOT_VENV=..\..\.venv\Scripts\python.exe
set LOCAL_VENV=.venv\Scripts\python.exe

if exist "%LOCAL_VENV%" (
  "%LOCAL_VENV%" app.py
  exit /b %ERRORLEVEL%
)

if exist "%ROOT_VENV%" (
  "%ROOT_VENV%" app.py
  exit /b %ERRORLEVEL%
)

python app.py
exit /b %ERRORLEVEL%
