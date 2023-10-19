SET mypath=%~dp0
cd %mypath:~0,-1%
ssh -i mykey -oStrictHostKeyChecking=no forensicinvestigator@192.168.1.112 -p 22
