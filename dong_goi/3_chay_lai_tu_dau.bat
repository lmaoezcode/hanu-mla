@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONDONTWRITEBYTECODE=1
set N=1
:find
if exist "output\experiments\lan-%N%" (set /a N+=1 & goto find)
set DIR=output\experiments\lan-%N%
echo Chay lai vao thu muc %DIR%. Ket qua goc khong bi doi.
echo.
python\python.exe scripts\run_sentence_baselines.py --phase select --output-dir "%DIR%"
if errorlevel 1 goto fail
python\python.exe scripts\run_sentence_baselines.py --phase test --output-dir "%DIR%"
if errorlevel 1 goto fail
python\python.exe scripts\verify_sentence_baselines.py --output-dir "%DIR%"
if errorlevel 1 goto fail
python\python.exe scripts\show_results.py --output-dir "%DIR%"
echo CHAY LAI XONG: %DIR%
pause
exit /b 0
:fail
echo.
echo CO LOI. Xem thong bao o tren.
pause
exit /b 1
