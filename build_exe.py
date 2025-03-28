import PyInstaller.__main__

PyInstaller.__main__.run([
    '--name=MouseClicker',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    'Mouse clicker.py'
])