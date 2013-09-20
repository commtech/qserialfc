import sys

from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages=['serialfc'], excludes=[], includes=['re'])


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable('qserialfc.py', base=base)
]

setup(name='qserialfc',
      version='1.2.2',
      options=dict(build_exe=buildOptions),
      executables=executables)
