@echo off
setlocal EnableExtensions
title Kanban Chat Server
cd /d "%~dp0"

set "PORT=8765"

rem --- Chon Python: uu tien "python", neu khong co thi "py -3" ---
set "PY="
where python >nul 2>nul && set "PY=python"
if not defined PY (
    where py >nul 2>nul && set "PY=py -3"
)
if not defined PY (
    echo [LOI] Khong tim thay Python. Hay cai Python va tick "Add Python to PATH".
    pause
    exit /b 1
)

rem --- Cong dang bi dung (server chay san) thi khong chay them ---
netstat -ano | findstr /R /C:":%PORT% .*LISTENING" >nul
if not errorlevel 1 (
    echo Server chat da chay san o cong %PORT%. Khong can chay lai.
    echo Quay lai ung dung Kanban va bam nut Chat de ket noi.
    pause
    exit /b 0
)

rem --- Mo cong tuong lua (can quyen Admin; khong du quyen thi bo qua) ---
netsh advfirewall firewall show rule name="Kanban Chat" >nul 2>nul
if errorlevel 1 (
    netsh advfirewall firewall add rule name="Kanban Chat" dir=in action=allow protocol=TCP localport=%PORT% >nul 2>nul
    if errorlevel 1 (
        echo [Luu y] Chua mo duoc tuong lua do thieu quyen Admin.
        echo         Neu may khac khong noi duoc, hay cho phep Python khi Windows hoi,
        echo         hoac chuot phai file nay chon "Run as administrator".
        echo.
    )
)

echo ==================================================
echo   MAY CHU CHAT KANBAN  (cong %PORT%)
echo   Cac may khac nhap mot trong cac IP sau:
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /C:"IPv4"') do echo        %%a
echo   (chi dung duoc khi cung Wi-Fi / mang LAN)
echo   DONG CUA SO NAY DE TAT SERVER.
echo ==================================================
echo.

%PY% chat_server.py --port %PORT%

echo.
echo Server da dung.
pause
