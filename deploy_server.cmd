@echo off
robocopy . \\srv-debian\OKanban /MIR /XF *.log *.log.* *.pyc /XD __pycache__ .git build dist .vscode
echo REDEMARRAGE DU SERVICE SUR SRV-DEBIAN
echo .
pause
ssh -t administrateur@srv-debian "sudo systemctl restart okanban_api.service"
