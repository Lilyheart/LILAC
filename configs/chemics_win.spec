# -*- mode: python -*-

block_cipher = None

# noinspection PyUnresolvedReferences
a = Analysis(['..\\chemics\\main.py'],
             pathex=['..\\chemics'],
             binaries=[],
             datas=[('..\\chemics\\assets\\icon.png', 'img')],
             hiddenimports=['scipy.constants'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['PyQt5'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

# noinspection PyUnresolvedReferences
pyz = PYZ(a.pure, a.zipped_data,
          cipher=block_cipher)

# noinspection PyUnresolvedReferences
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='chemics.2.2.6',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True,
          icon='..\\chemics\\assets\\icon.ico')
