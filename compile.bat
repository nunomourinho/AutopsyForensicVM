SET mypath=%~dp0
cd %mypath:~0,-1%
call env_forensicEnv\scripts\activate.bat
rem pyinstaller --noconfirm --onefile --console --icon "forensicVMClient.ico"  --clean -"forensicVmClient.py"
pyinstaller --hidden-import chardet --hidden-import charset_normalizer.md__mypyc --noconfirm --onefile --icon "forensicVMClient.ico" --clean  "forensicVmClient.py"
move dist\forensicVmClient.exe forensicVmClient.exe
pause
