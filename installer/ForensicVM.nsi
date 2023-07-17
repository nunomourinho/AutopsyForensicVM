!include "MUI2.nsh"

!define PRODUCT_NAME "ForensicVM"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_DIR "${PRODUCT_NAME}"

!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_RIGHT

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
;!insertmacro MUI_PAGE_LICENSE ""
; Components page
!insertmacro MUI_PAGE_COMPONENTS
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!insertmacro MUI_PAGE_FINISH

;Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "${PRODUCT_NAME}.exe"
InstallDir "$APPDATA\Autopsy\Python_modules\${PRODUCT_DIR}"
ShowInstDetails show
ShowUnInstDetails show

Section "ForensicVM Client" SEC01
    SetOutPath "$APPDATA\Autopsy\Python_modules\${PRODUCT_DIR}"
    SetOverwrite try
    File /r "..\dist\forensicVmClient.exe"
    File /r "..\dist\forensicVMProd.py"    

    ; Create a shortcut on the Start menu
    CreateShortCut "$SMPROGRAMS\${PRODUCT_NAME}.lnk" "$INSTDIR\${PRODUCT_DIR}\forensicVmClient.exe"
	
    ; Write the uninstall keys for Windows
    WriteUninstaller "$INSTDIR\${PRODUCT_DIR}\Uninstall.exe"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "DisplayName" "${PRODUCT_NAME} ${PRODUCT_VERSION}"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}" "UninstallString" "$INSTDIR\${PRODUCT_DIR}\Uninstall.exe"

SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\${PRODUCT_DIR}\Uninstall.exe"
    Delete "$INSTDIR\${PRODUCT_DIR}\forensicVmClient.exe"
    Delete "$INSTDIR\${PRODUCT_DIR}\forensicVMProd.py"    
    Delete "$SMPROGRAMS\${PRODUCT_NAME}.lnk"

    ; Remove the uninstall keys for Windows
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
    !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "ForensicVM Client"
!insertmacro MUI_FUNCTION_DESCRIPTION_END
