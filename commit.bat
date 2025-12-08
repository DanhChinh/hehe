@echo off
echo git add...
git add . :!AI/__pycache__/

echo git config --global user.email "danhchinh2024@gmail.com"
git config --global user.email "danhchinh2024@gmail.com"

echo git config --global user.name "chinh"
git config --global user.name "chinh"

echo git commit -m "Auto commit: %date% %time%"
git commit -m "Auto commit: %date% %time%"

echo git push origin main
git push origin main --force

echo Done!
pause