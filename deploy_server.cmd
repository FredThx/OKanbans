@echo off
robocopy . \\srv-debian\OKanban /MIR /XF *.log *.log.* *.pyc /XD __pycache__ .git build dist .vscode
echo IL FAUT MAINTENANT REDEMARRER LE SERVICE SUR SRV-DEBIAN
echo sudo systemctl restart okanban_api.service
echo .