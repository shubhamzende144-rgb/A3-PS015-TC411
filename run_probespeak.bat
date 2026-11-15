@echo off
cd /d "%~dp0"
py -3 -m pip install -r requirements-desktop.txt
set PYTHONPATH=src;agent
py -3 -m probespeak
