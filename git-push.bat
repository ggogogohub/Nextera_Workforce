@echo off
set /p desc=Commit message: 
if "%desc%"=="" set desc=Auto-commit on %date% %time%
git add .
git commit -m "%desc%"
git push origin master
