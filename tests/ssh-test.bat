SET mypath=%~dp0
cd %mypath:~0,-1%
ssh -oStrictHostKeyChecking=no forensicinvestigator@85.240.2.211 -p 8228 -R 4451:localhost:445 -i mykey "ls"
pause