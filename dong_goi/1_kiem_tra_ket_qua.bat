@echo off
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONDONTWRITEBYTECODE=1
python\python.exe scripts\show_results.py
python\python.exe scripts\verify_sentence_baselines.py
if errorlevel 1 (echo. & echo KIEM TRA KHONG DAT. Xem thong bao o tren.) else (echo. & echo KIEM TRA DAT: all_passed = true)
pause
