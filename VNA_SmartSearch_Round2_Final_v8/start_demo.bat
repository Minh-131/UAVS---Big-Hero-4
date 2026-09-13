@echo off
cd /d "%~dp0"
py smoke_test.py || exit /b 1
py run.py
