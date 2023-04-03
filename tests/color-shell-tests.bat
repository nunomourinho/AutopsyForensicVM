SET mypath=%~dp0
cd %mypath:~0,-1%
call ../forensicEnv\scripts\activate.bat
python color-shell.py
pause