SET mypath=%~dp0
cd %mypath:~0,-1%
rem ssh -i mykey -oStrictHostKeyChecking=no forensicinvestigator@85.240.2.211 -p 8228 -R 4451:localhost:445 "ls -alh"
python shell.py
pause