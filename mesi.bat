SET mypath=%~dp0
cd %mypath:~0,-1%
rem cd C:\Users\admlocal\Documents\GitHub\forensicVM\main\autopsy-plugin
call forensicEnv\scripts\activate.bat
python forensicVmClient.py %*
