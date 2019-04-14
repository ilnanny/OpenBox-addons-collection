from distutils.core import setup
setup(name='obMenu',
      version='1.0',
      description='Openbox Menu Editor',
      author='Manuel Colmenero',
      author_email='m.kolme@gmail.com',
      scripts=['obmenu'],
	  py_modules=['obxml'],
	  data_files=[('/usr/local/share/obmenu', ['obmenu.glade', 'icons/mnu16.png', 'icons/mnu48.png'])]
      )

