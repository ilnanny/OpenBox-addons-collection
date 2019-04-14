
'''setup.py component of obmenux installer
 this is for a complete setup, including the pipe menu scripts,
 for use with `install` option, to install obmenux complete, e.g.
 `sudo python2 setup.py install`
 
 typical effect:
     writes scripts to /usr/local/bin
     and data files to /usr/local/share/obmenux
     and module to     /usr/local/lib/python-[version]/dist-packages
         along with metadata file obmenux-[version].egg-info
'''

from distutils.core import setup
import os

if os.path.isfile('cleanup.py'):
	os.system('python2 cleanup.py clean --all')

libdir = 'share/obmenux'

setup(name='obmenux',
      version='1.3.0',
      description='Openbox Menu Editor X',
      long_description=
      'an Openbox menu editor called Openbox Menu Editor X or obmenux',
      license='GPL',
      url='https://github.com/sderaut/obmenux',
      author='SDE',
      author_email='sonnymoonie@gmail.com',
      platforms=['Linux'], 
      scripts=['obmenux', 'pipes/obmx-xdg','pipes/obmx-dir','pipes/obmx-moz',
               'pipes/obmx-nav'],
      py_modules=['obxmlx'],
      data_files=[(libdir,
                   ['gfx/obmenux.glade', 'gfx/mnu16.png','gfx/mnu48.png'])])
