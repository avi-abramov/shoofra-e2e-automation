@echo off
powershell -ExecutionPolicy Bypass -File "%~dp0test-fast.ps1" %*
exit /b %ERRORLEVEL%
