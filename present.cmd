@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0present.ps1" %*
exit /b %ERRORLEVEL%
