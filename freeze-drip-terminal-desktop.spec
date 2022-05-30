import os
import pathlib


block_cipher = None
qt_plugins_path = (str(pathlib.Path('.venv/Lib/site-packages/PySide6/plugins')), str(pathlib.Path('PySide6/plugins'))) if os.name == 'nt' \
    else(str(pathlib.Path('.venv/lib/python3.10/site-packages/PySide6/Qt/plugins')), str(pathlib.Path('PySide6/Qt/plugins')))

a = Analysis([str(pathlib.Path('.venv') / ('Scripts' if os.name == 'nt' else 'bin') / 'freeze-drip-terminal-desktop')],
             pathex=[pathlib.Path(SPECPATH).resolve().parent],
             binaries=[],
             datas=[
                 qt_plugins_path,
                 (str(pathlib.Path('packages/desktop/ui/main_window.ico')), str(pathlib.Path('desktop/ui'))),
                 (str(pathlib.Path('packages/desktop/ui/main_window.ui')), str(pathlib.Path('desktop/ui'))),
                 (str(pathlib.Path('packages/desktop/ui/received_form.ui')), str(pathlib.Path('desktop/ui')))],
             hiddenimports=[],
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
          name='FreezeDripTerminalDesktop',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon=str(pathlib.Path('packages/desktop/ui/main_window-512x512.ico')))

# vim: filetype=python
