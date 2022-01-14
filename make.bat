@echo off
python make_properties.py
pyinstaller ^
  --onefile ^
  --noconsole ^
  --noupx ^
  --win-private-assemblies ^
  --icon=.\okanbans.ico ^
  --noconfirm ^
  --version-file=properties.rc ^
  okanbans.py
pause
