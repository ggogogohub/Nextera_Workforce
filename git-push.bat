@echo off
set /p desc=Commit message:
git add .
git commit -m "%desc%"
git push origin main
