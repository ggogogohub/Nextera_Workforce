@echo off
:loop
timeout /t 5
call git-push.bat
goto loop
