@echo off
echo 🛠️  OZARK FINANCES - AUDIT LOGS RESET
echo =====================================
echo.

cd /d "%~dp0"

echo Running audit logs reset utility...
python reset_audit_logs.py %*

echo.
echo Press any key to close...
pause >nul
