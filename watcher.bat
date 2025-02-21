@echo off
setlocal
:loop
timeout /t 30 /nobreak >nul  ⬅ Fix timeout command
call git-push.bat
goto loop
