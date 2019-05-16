    
from setuptools import setup, find_packages
import glob
import os
import subprocess
import sys
import shutil

board = os.environ['BOARD']
board_folder = 'boards/{}/'.format(board)

if os.geteuid() != 0:
    print("This program must be run as root. Aborting.")
    sys.exit(1)

if board != 'Pynq-Z2':
    print("Only supported on a Pynq-Z2 Board")
    exit(1)

setup(
	name = "pynq_iot_demo",
	version = 1.0,
	url = 'https://github.com/xupsh/PYNQ-IoT-demo',
	license = 'BSD 3-Clause License',
	author = "Cong Zou",
	author_email = "congzou2021@u.northwestern.edu",

	packages = find_packages(),
	package_data = {
	'' : ['*.bit','*.tcl','*.py','*.bin','*.txt', '*.cpp', '*.h', '*.sh'],
	},
	description = "Some demo based on PYNQ-Z2",
    install_requires=[
        'pynq','numpy'
    ],
)

if 'install' in sys.argv:
	if os.path.isdir(os.environ["PYNQ_JUPYTER_NOTEBOOKS"]+"/pynq-iot/"):
		shutil.rmtree(os.environ["PYNQ_JUPYTER_NOTEBOOKS"]+"/pynq-iot/")
	shutil.copytree("notebooks",os.environ["PYNQ_JUPYTER_NOTEBOOKS"]+"/pynq-iot/")

	for f in os.listdir(os.path.join(board_folder, 'lib/arduino/')):
		if os.path.isfile(os.path.join('/usr/local/lib', os.environ['PYNQ_PYTHON'], 'dist-packages/pynq/lib/arduino', f)):
			os.remove(os.path.join('/usr/local/lib', os.environ['PYNQ_PYTHON'], 'dist-packages/pynq/lib/arduino', f))
		shutil.copyfile(os.path.join(board_folder, 'lib/arduino/', f) ,os.path.join('/usr/local/lib', os.environ['PYNQ_PYTHON'], 'dist-packages/pynq/lib/arduino', f)) #copy lib

