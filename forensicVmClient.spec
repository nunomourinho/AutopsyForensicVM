# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(['forensicVmClient.py'],
             pathex=[],
             binaries=[('create_user_and_share.bat', '.'), ('forensicVMClient.png', '.'), ('nircmdc.exe', '.'), ('ssh.exe', '.'), ('forensicVMClient.ico', '.'), ('libcrypto.dll', '.')],
             datas=[],
             hiddenimports=['chardet', 'charset_normalizer.md__mypyc'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
splash = Splash('forensicVMClient.png',
                binaries=a.binaries,
                datas=a.datas,
                text_pos=None,
                text_size=12,
                minify_script=True)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas, 
          splash, 
          splash.binaries,
          [],
          name='forensicVmClient',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='forensicVMClient.ico')
