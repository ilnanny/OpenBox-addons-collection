#!/usr/bin/python

import os, sys, glob, fnmatch

## Added 10 Jan 2008

try: 
    from distutils.core import setup, Extension
    import distutils.command.install_data
    from distutils.core import setup
except:
    print "DistUtils / SetupTools are required"
    sys.exit(1)

try:
    from DistUtilsExtra.command import *
except:
    print "DistUtils Extras is required"
    sys.exit(1)

setup(name = "oblogout",
    version = "0.3",
    description = "Openbox Logout",
    author = "Andrew Williams",
    author_email = "andy@tensixtyone.com",
    url = "http://launchpad.net/oblogout/",
    
    packages = ['oblogout'],
    scripts = ["data/oblogout"],
    data_files = [('share/themes/simplistic/oblogout', glob.glob('data/themes/simplistic/oblogout/*')),
                 ('share/themes/oxygen/oblogout', glob.glob('data/themes/oxygen/oblogout/*')),
                 ('/etc', glob.glob('data/oblogout.conf'))],
    
    cmdclass = { 'build' : build_extra.build_extra,
                 'build_i18n' :  build_i18n.build_i18n },


    long_description = """Really long text here."""     
) 
