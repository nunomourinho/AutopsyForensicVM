SET mypath=%~dp0
cd %mypath:~0,-1%
call env_forensicEnv\scripts\activate.bat
pyinstaller --noconfirm --onefile --console --icon "forensicVMClient.ico"  --clean  "forensicVmClient.py"
move dist\forensicVmClient.exe forensicVmClient.exe
pause
