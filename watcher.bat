@echo off
setlocal
:loop
timeout /t 30 >nul  ⬅ (Runs every 30 seconds)
call git-push.bat
goto loop
