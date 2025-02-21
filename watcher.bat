@echo off
setlocal
:loop
timeout /t 30 >nul
call git-push.bat
goto loop
