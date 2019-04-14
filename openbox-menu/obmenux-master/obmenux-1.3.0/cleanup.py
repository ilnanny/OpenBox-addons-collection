
''' cleanup.py
 This script is only for other scripts in the same installer folder to run
 `python2 cleanup.py clean -all`
 because distutils setup unfortunately has the behavior of reinstalling scripts
 previously installed despite not requesting them or despite providing changed
 versions. This script is designed to be safer and more maintainable than
 alternate ways of attempting a correct installation.
'''

from distutils.core import setup

setup(name='cleanup',
      version='0.0.1',
      description='installer folder cleanup script',
      long_description='a script for cleaning up an installer folder',
      license='GPL',
      url='https://github.com/sderaut/obmenux',
      author='SDE',
      author_email='sonnymoonie@gmail.com',
      platforms=['Linux'], 
      scripts=[],
      py_modules=[],
      data_files=[])
