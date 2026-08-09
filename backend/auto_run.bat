@echo off
echo pip install -r requirements.txt
pip install -r requirements.txt

echo python update_db.py
python update_db.py

echo python index.py
python index.py