@echo off
setlocal

set username=%~1
set password=%~2
set sharename=%~3
set folderpath=%~4

echo Checking if user already exists...
net user "%username%" >nul 2>&1
if %errorlevel% equ 0 (
    echo User "%username%" already exists.
    net user "%username%" /expires:never
    net user "%username%" /expires:never
    WMIC USERACCOUNT WHERE Name='%username%' SET PasswordExpires=FALSE
) else (
    echo User "%username%" does not exist. Creating user...
    net user "%username%" "%password%" /add /y
    net user "%username%" /expires:never
    net localgroup Administradores "%username%" /add /y
	net localgroup Administrators "%username%" /add /y
    net user "%username%" /expires:never
    WMIC USERACCOUNT WHERE Name='%username%' SET PasswordExpires=FALSE
)

echo Checking if folder already exists...
if exist "%folderpath%" (
    echo Folder "%folderpath%" already exists.
) else (
    echo Folder "%folderpath%" does not exist.
)

echo Setting permissions on folder...
icacls "%folderpath%" /grant "%username%":(R,X) /T>nul

echo Creating share...
echo net share "%sharename%"="%folderpath%" /cache:none /grant:"%username%",read
net share "%sharename%"="%folderpath%"  /cache:none /grant:"%username%",read

echo Share created successfully.

endlocal
pause

