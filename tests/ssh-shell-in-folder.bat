SET mypath=%~dp0
cd %mypath:~0,-1%
ssh -t -i mykey -oStrictHostKeyChecking=no forensicinvestigator@85.240.2.211 -p 8228 "cd /forensicVM/mnt/vm/9b309b16-ad74-5d86-9879-273873a795c1; exec bash"
