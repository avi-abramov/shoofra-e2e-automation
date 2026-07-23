@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0test-all.ps1" %*
exit /b %ERRORLEVEL%
