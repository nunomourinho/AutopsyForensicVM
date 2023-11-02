SET mypath=%~dp0
cd %mypath:~0,-1%
call env_forensicEnv\scripts\activate.bat

pyinstaller --hidden-import chardet --hidden-import charset_normalizer.md__mypyc --noconfirm --onefile --icon "forensicVMClient.ico" --clean  "forensicVmClient.py" --add-binary create_user_and_share.bat;. --add-binary forensicVMClient.png;. --add-binary nircmdc.exe;. --add-binary ssh.exe;. --add-binary forensicVMClient.ico;. --add-binary libcrypto.dll;. -w --splash "forensicVMClient.png"

copy forensicVMProd.py-dist dist\forensicVMProd.py






rem pyinstaller --hidden-import chardet --hidden-import charset_normalizer.md__mypyc --noconfirm --onefile --icon "forensicVMClient.ico" --clean  "forensicVmClient.py" -w --splash "forensicVMClient.png" --add-binary create_user_and_share.bat;. --add-binary forensicVMClient.png;. --add-binary nircmdc.exe;. --add-binary ssh.exe;. --add-binary forensicVMClient.ico;. --add-binary libcrypto.dll;.


copy dist\forensicVmClient.exe forensicVmClient.exe

rem pyinstaller forensicVmClient.spec

rem pyinstaller --hidden-import chardet --hidden-import charset_normalizer.md__mypyc --noconfirm --onefile --icon "forensicVMClient.ico" --clean  "forensicVmClient.py" -w --splash "forensicVMClient.png" 

rem pyinstaller --hidden-import chardet --hidden-import charset_normalizer.md__mypyc --noconfirm --onedir --icon "forensicVMClient.ico" --clean  "forensicVmClient.py" --splash "forensicVMClient.png" --add-binary forensicVMClient.png;. -w

pause