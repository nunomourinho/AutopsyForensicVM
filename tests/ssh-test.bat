SET mypath=%~dp0
cd %mypath:~0,-1%
ssh -t -i mykey -oStrictHostKeyChecking=no forensicinvestigator@85.240.2.211 -p 8228 "mc"
ssh -i mykey -oStrictHostKeyChecking=no forensicinvestigator@85.240.2.211 -p 8228
