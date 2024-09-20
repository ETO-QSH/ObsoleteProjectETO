import os, subprocess

imgfile, zipfile, output = r'Firefly 20240911212634.png', r'Firefly.zip', r'output.png'

os.system('chcp 65001')
subprocess.run(['cmd', '/c', 'copy', '/b', imgfile, '+', zipfile, output])
