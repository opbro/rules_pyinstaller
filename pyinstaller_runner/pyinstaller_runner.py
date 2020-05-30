import argparse
import os
import os.path
import sys
import zipfile
import tempfile
import time
import subprocess
import shutil

def write_python_spec(paths, main, outfile, spec_file):
    exe_outfile = outfile.split('.')[0]
    main_abs_path = os.path.abspath(main).replace('\\', '\\\\')
    spec_template = f"""
# -*- mode: python ; coding: utf-8 -*-
block_cipher = None
a = Analysis(['{main_abs_path}'],
             pathex={paths},
             binaries=[],
             datas=[],
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
          name='{exe_outfile}',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )
"""
    with open(spec_file, 'w') as _file:
        _file.write(spec_template)
    



def main():
    my_env = os.environ

    parser = argparse.ArgumentParser(description='Builds a python executable using pyinstaller.exe')
    parser.add_argument('--wheel', type=str, action='append')
    parser.add_argument('--outfile', type=str, required=True)
    parser.add_argument('--main', type=str, required=True)
    parser.add_argument('--userpath', type=str, required=True)
    parser.add_argument('--debuglevel', type=str, default="WARN")
    arguments = parser.parse_args(sys.argv[1:])
    my_env['PATH'] = arguments.userpath
    tmp_dirs = []
    for _wheel in arguments.wheel:
        tmp_dir = tempfile.TemporaryDirectory()      
        with zipfile.ZipFile(_wheel) as zip_ref: 
            zip_ref.extractall(tmp_dir.name)
        tmp_dirs.append(tmp_dir.name)
    tmp_spec_file = tempfile.NamedTemporaryFile(suffix='.spec', mode='w', delete=False)
    base_outfile = os.path.basename(arguments.outfile)
    write_python_spec(tmp_dirs, arguments.main, base_outfile, tmp_spec_file.name)
    tmp_spec_file.close()
    proc = subprocess.Popen("pyinstaller.exe --log-level " + arguments.debuglevel + " --clean --distpath . --onefile " + tmp_spec_file.name, shell=True)
    proc.communicate()
    shutil.move(base_outfile, arguments.outfile)
    os.unlink(tmp_spec_file.name)

if __name__ == "__main__":
    main()