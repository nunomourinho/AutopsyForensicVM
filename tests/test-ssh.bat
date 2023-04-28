SET mypath=%~dp0
cd %mypath:~0,-1%

ssh.exe -t -i mykey -oStrictHostKeyChecking=no forensicinvestigator@85.240.2.211 -p 8228 -R 42673:127.0.0.1:445 sudo /forensicVM/bin/run-or-convert.sh --windows-share si4 --share-login qemu-master-user --share-password secretPsw0rd!!! --forensic-image-path //./E: --folder-uuid 7b4d448f-fc68-58c2-9ad9-de9195d75d65 --copy copy --share-port 42673
pause