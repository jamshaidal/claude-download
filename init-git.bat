@echo off
echo Initializing Git repository...
git init
git add .
git commit -m "Initial commit"
echo.
echo Repository initialized!
echo.
echo Next steps:
echo 1. Create a new repository on GitHub (https://github.com/new)
echo 2. Link this repository:
echo    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
echo 3. Push:
echo    git branch -M main
echo    git push -u origin main
echo.
pause