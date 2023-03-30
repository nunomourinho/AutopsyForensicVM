SET mypath=%~dp0
cd %mypath:~0,-1%
ssh forensicinvestigator@85.240.2.211 -p 8228 -R 4450:localhost:445 -i mykey
cmd /p