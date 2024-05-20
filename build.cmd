@echo off
:: https://gregoryszorc.com/docs/python-build-standalone/main/index.html
setlocal
cd /D "%~dp0"
"%~dp0\python\scripts\pyinstaller" --onefile --windowed --name Mortgage --paths "%~dp0\main.py"
::move %~dp0\dist\*.exe %~dp0\pyapp_dist
::%~dp0\scripts\upx --force plcscan.exe