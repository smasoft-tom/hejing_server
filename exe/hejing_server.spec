# -*- mode: python -*-

block_cipher = None


a = Analysis(['hejing_server.py'],
             pathex=['.\\core\\tools\\reg', '.\\core', 'C:\\Users\\SmaSoft_Tom_Laptop\\Documents\\smaai_trainer_4\\Main\\exe'],
             binaries=[],
             datas=[],
             hiddenimports=['scipy._lib.messagestream', 'cytoolz.utils', 'cytoolz._signatures','pkg_resources.py2_warn'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='hejing_server',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          runtime_tmpdir=None,
          console=True , icon='smaai.ico')
