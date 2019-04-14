#!/usr/bin/python

# test DistUtilsExtra.auto

import unittest, shutil, tempfile, os, os.path, subprocess, re

class T(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.src = tempfile.mkdtemp()

        self._mksrc('setup.py', '''
# ignore warning about import from local path
import warnings
warnings.filterwarnings('ignore', 'Module DistUtilsExtra was already imported from.*')
warnings.filterwarnings('ignore', 'pipe2 set errno ENOSYS.*')

from DistUtilsExtra.auto import setup

setup(
    name='foo',
    version='0.1',
    description='Test suite package',
    url='https://foo.example.com',
    license='GPL v2 or later',
    author='Martin Pitt',
    author_email='martin.pitt@example.com',
)
''')
        self.snapshot = None
        self.install_tree = None

    def tearDown(self):
        try:
            # check that setup.py clean removes everything
            (o, e, s) = self.setup_py(['clean', '-a'])
            self.assertEqual(s, 0, o+e)
            cruft = self.diff_snapshot()
            self.assertEqual(cruft, '', 'no cruft after cleaning:\n' + cruft)
        finally:
            shutil.rmtree(self.src)
            if self.snapshot:
                shutil.rmtree(self.snapshot)
            if self.install_tree:
                shutil.rmtree(self.install_tree)
            self.src = None
            self.snapshot = None
            self.install_tree = None

    #
    # actual tests come here
    #

    def test_empty(self):
        '''empty source tree (just setup.py)'''

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertFalse('following files are not recognized' in o)

        f = self.installed_files()
        # just installs the .egg_info
        self.assertEqual(len(f), 1)
        self.assertTrue(f[0].endswith('.egg-info'))

    def test_vcs(self):
        '''Ignores revision control files'''

        self._mksrc('.shelf/1')
        self._mksrc('.bzr/revs')
        self._mksrc('.git/config')
        self._mksrc('.svn/revs')

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertFalse('following files are not recognized' in o)

        f = self.installed_files()
        # just installs the .egg_info
        self.assertEqual(len(f), 1)
        self.assertTrue(f[0].endswith('.egg-info'))

    def test_modules(self):
        '''Python modules'''

        self._mksrc('yesme.py', b'x ="a\xc3\xa4b\xe2\x99\xa5"'.decode('UTF-8'))
        self._mksrc('stuff/notme.py', b'x ="a\xc3\xa4b\xe2\x99\xa5"'.decode('UTF-8'))
        self._mksrc('stuff/withencoding.py', b'# -*- Mode: Python; coding: utf-8; -*- \nfoo = 1'.decode('UTF-8'))

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertTrue('following files are not recognized' in o)
        self.assertTrue('\n  stuff/notme.py\n' in o)

        f = '\n'.join(self.installed_files())
        self.assertTrue('-packages/yesme.py' in f)
        self.assertFalse('notme' in f)

    def test_packages(self):
        '''Python packages'''

        self._mksrc('foopkg/__init__.py', '')
        self._mksrc('foopkg/bar.py')
        self._mksrc('foopkg/baz.py')
        self._mksrc('noinit/notme.py')

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertTrue('following files are not recognized' in o)
        self.assertTrue('\n  noinit/notme.py\n' in o)

        f = '\n'.join(self.installed_files())
        self.assertTrue('foopkg/__init__.py' in f)
        self.assertTrue('foopkg/bar.py' in f)
        self.assertFalse('noinit' in f)

    def test_dbus(self):
        '''D-BUS configuration and service files'''

        # D-BUS ACL configuration file
        self._mksrc('daemon/com.example.foo.conf', '''<!DOCTYPE busconfig PUBLIC
 "-//freedesktop//DTD D-BUS Bus Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/dbus/1.0/busconfig.dtd">
<busconfig>
</busconfig>''')

        # non-D-BUS configuration file
        self._mksrc('daemon/defaults.conf', 'start = True\nlog = syslog')

        # D-BUS system service
        self._mksrc('daemon/com.example.foo.service', '''[D-BUS Service]
Name=com.example.Foo
Exec=/usr/lib/foo/foo_daemon
User=root''')

        # D-BUS session service
        self._mksrc('gui/com.example.foo.gui.service', '''[D-BUS Service]
Name=com.example.Foo.GUI
Exec=/usr/bin/foo-gtk
''')

        # non-D-BUS .service file
        self._mksrc('stuff/super.service', 'I am a file')

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertTrue('following files are not recognized' in o)
        self.assertTrue('\n  stuff/super.service\n' in o)

        f = self.installed_files()
        self.assertEqual(len(f), 4) # 3 D-BUS files plus .egg-info
        self.assertTrue('/etc/dbus-1/system.d/com.example.foo.conf' in f)
        self.assertTrue('/usr/share/dbus-1/system-services/com.example.foo.service' in f)
        self.assertTrue('/usr/share/dbus-1/services/com.example.foo.gui.service' in f)
        self.assertFalse('super.service' in '\n'.join(f))

    def test_gsettings(self):
        '''GSettings schema files'''

        # schema files in dedicated directory
        self._mksrc('data/glib-2.0/schemas/org.test.myapp.gschema.xml')
        self._mksrc('data/glib-2.0/schemas/gschemas.compiled')
        # schema files in data directory
        self._mksrc('data/org.test.myapp2.gschema.xml')
        self._mksrc('data/gschemas.compiled')

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)

        f = self.installed_files()
        self.assertEqual(len(f), 3) # 2 schema files plus .egg-info
        self.assertTrue('/usr/share/glib-2.0/schemas/org.test.myapp.gschema.xml' in f)
        self.assertFalse('gschemas.compiled' in '\n'.join(f))

    def test_apport_hook(self):
        '''Apport hooks'''

        self._mksrc('apport/foo.py', '''import os, apport
def add_info(report):
    pass
''')

        self._mksrc('apport/source_foo.py', '''import os, apport
def add_info(report):
    pass
''')

        (o, e, s) = self.do_install()
        self.assertFalse('following files are not recognized' in o, o)
        
        f = self.installed_files()
        self.assertEqual(len(f), 3, f) # 2 hook files plus .egg-info
        self.assertTrue('/usr/share/apport/package-hooks/foo.py' in f, f)
        self.assertTrue('/usr/share/apport/package-hooks/source_foo.py' in f, f)
        
    def test_po(self):
        '''gettext *.po files'''

        self._mkpo()

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertFalse('following files are not recognized' in o)
        f = self.installed_files()
        self.assertTrue('/usr/share/locale/de/LC_MESSAGES/foo.mo' in f)
        self.assertTrue('/usr/share/locale/fr/LC_MESSAGES/foo.mo' in f)
        self.assertFalse('junk' in '\n'.join(f))

        msgunfmt = subprocess.Popen(['msgunfmt',
            os.path.join(self.install_tree,
            'usr/share/locale/de/LC_MESSAGES/foo.mo')],
            stdout=subprocess.PIPE)
        out = msgunfmt.communicate()[0].decode()
        self.assertEqual(out, self._src_contents('po/de.po'))

    def test_policykit(self):
        '''*.policy.in PolicyKit files'''

        self._mksrc('daemon/com.example.foo.policy.in', '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
 "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/PolicyKit/1.0/policyconfig.dtd">
<policyconfig>
  <vendor>Foo project</vendor>
  <vendor_url>https://foo.example.com</vendor_url>

  <action id="com.example.foo.greet">
    <_description>Good morning</_description>
    <_message>Hello</_message>
    <defaults>
      <allow_active>yes</allow_active>
    </defaults>
  </action>
</policyconfig>''')

        self._mkpo()
        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertFalse('following files are not recognized' in o)

        f = self.installed_files()
        self.assertTrue('/usr/share/polkit-1/actions/com.example.foo.policy' in f)
        p = self._installed_contents('usr/share/polkit-1/actions/com.example.foo.policy')
        self.assertTrue('<description>Good morning</description>' in p)
        self.assertTrue('<description xml:lang="de">Guten Morgen</description>' in p)
        self.assertTrue('<message>Hello</message>' in p)
        self.assertTrue('<message xml:lang="de">Hallo</message>' in p)

    def test_desktop(self):
        '''*.desktop.in files'''

        self._mksrc('gui/foogtk.desktop.in', '''[Desktop Entry]
_Name=Hello
_Comment=Good morning
Exec=/bin/foo''')
        self._mksrc('gui/autostart/fooapplet.desktop.in', '''[Desktop Entry]
_Name=Hello
_Comment=Good morning
Exec=/usr/bin/fooapplet''')
        self._mkpo()
        self._mksrc('data/foosettings.desktop.in', '''[Desktop Entry]
_Name=Hello
_Comment=Good morning
Exec=/bin/foosettings''')

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertFalse('following files are not recognized' in o)

        f = self.installed_files()
        self.assertTrue('/usr/share/autostart/fooapplet.desktop' in f)
        self.assertTrue('/usr/share/applications/foogtk.desktop' in f)
        self.assertTrue('/usr/share/applications/foosettings.desktop' in f)
        # data/*.desktop.in shouldn't go to data dir
        self.assertFalse('/usr/share/foo/' in f)

        p = self._installed_contents('usr/share/autostart/fooapplet.desktop')
        self.assertTrue('\nName=Hello\n' in p)
        self.assertTrue('\nName[de]=Hallo\n' in p)
        self.assertTrue('\nComment[fr]=Bonjour\n' in p)

    def test_icons(self):
        '''data/icons/'''

        self._mksrc('data/icons/scalable/actions/press.png')
        self._mksrc('data/icons/48x48/apps/foo.png')
        scalable_icon_path = os.path.join(self.src, 'data', 'icons', 'scalable')
        os.symlink(os.path.join(scalable_icon_path, 'actions', 'press.png'),
                os.path.join(scalable_icon_path, 'actions', 'crunch.png'))

        # test broken symlink, too
        os.mkdir(os.path.join(scalable_icon_path, 'mimetypes'))
        os.symlink('../apps/foo.svg', 
                os.path.join(scalable_icon_path, 'mimetypes', 'text-x-foo.svg'))

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertFalse('following files are not recognized' in o)

        f = self.installed_files()
        self.assertTrue('/usr/share/icons/hicolor/scalable/actions/press.png' in f)
        self.assertTrue('/usr/share/icons/hicolor/scalable/actions/crunch.png' in f)
        self.assertTrue('/usr/share/icons/hicolor/48x48/apps/foo.png' in f)
        self.assertTrue(os.path.islink(os.path.join(self.install_tree, 
           'usr/share/icons/hicolor/scalable/actions/crunch.png')))
        self.assertTrue(os.path.islink(os.path.join(self.install_tree, 
           'usr/share/icons/hicolor/scalable/mimetypes/text-x-foo.svg')))

    def test_data(self):
        '''Auxiliary files in data/'''

        # have some explicitly covered files, to check that they don't get
        # installed into prefix/share/foo/ again
        self._mksrc('setup.py', '''
from DistUtilsExtra.auto import setup
from glob import glob

setup(
    name='foo',
    version='0.1',
    description='Test suite package',
    url='https://foo.example.com',
    license='GPL v2 or later',
    author='Martin Pitt',
    author_email='martin.pitt@example.com',

    data_files = [
      ('/lib/udev/rules.d', ['data/40-foo.rules']),
      ('/etc/foo', glob('data/*.conf')),
    ]
)
''')

        self._mksrc('data/stuff')
        self._mksrc('data/handlers/red.py', 'import sys\nprint ("RED")')
        self._mksrc('data/handlers/blue.py', 'import sys\nprint ("BLUE")')
        self._mksrc('data/40-foo.rules')
        self._mksrc('data/blob1.conf')
        self._mksrc('data/blob2.conf')
        os.symlink('stuff', os.path.join(self.src, 'data', 'stufflink'))

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertFalse('following files are not recognized' in o, o)

        f = self.installed_files()
        self.assertTrue('/usr/share/foo/stuff' in f)
        self.assertTrue('/usr/share/foo/stufflink' in f)
        self.assertTrue(os.path.islink(os.path.join(self.install_tree, 'usr',
            'share', 'foo', 'stufflink')))
        self.assertTrue('/usr/share/foo/handlers/red.py' in f)
        self.assertTrue('/usr/share/foo/handlers/blue.py' in f)
        self.assertTrue('/lib/udev/rules.d/40-foo.rules' in f)
        self.assertTrue('/etc/foo/blob1.conf' in f)
        self.assertTrue('/etc/foo/blob2.conf' in f)
        self.assertFalse('/usr/share/foo/blob1.conf' in f)
        self.assertFalse('/usr/share/foo/40-foo.rules' in f)

    def test_scripts(self):
        '''scripts'''

        # these should get autoinstalled
        self._mksrc('bin/yell', '#!/bin/sh', True)
        self._mksrc('bin/shout', '#!/bin/sh', True)
        self._mksrc('bin/foo', b'#!/usr/bin/python\n# \xc2\xa9 copyright'.decode('UTF-8'), True)
        os.symlink('shout', os.path.join(self.src, 'bin', 'shoutlink'))

        # these shouldn't
        self._mksrc('daemon/food', '#!/bin/sh', True) # not in bin/
        self._mksrc('foob', '#!/bin/sh', True) # not named like project
        # not executable
        self._mksrc('bin/whisper', b'#!/usr/bin/python\n# \xc2\xa9 copyright'.decode('UTF-8'))

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertTrue('following files are not recognized' in o)
        self.assertTrue('\n  foob' in o)
        self.assertTrue('\n  bin/whisper' in o)
        self.assertTrue('\n  daemon/food' in o)

        f = self.installed_files()
        self.assertTrue('/usr/bin/yell' in f)
        self.assertTrue('/usr/bin/shout' in f)
        self.assertTrue('/usr/bin/shoutlink' in f)
        self.assertTrue(os.path.islink(os.path.join(self.install_tree, 'usr',
            'bin', 'shoutlink')))
        self.assertTrue('/usr/bin/foo' in f)
        ftext = '\n'.join(f)
        self.assertFalse('food' in ftext)
        self.assertFalse('foob' in ftext)
        self.assertFalse('whisper' in ftext)

        # verify that they are executable
        binpath = os.path.join(self.install_tree, 'usr', 'bin')
        self.assertTrue(os.access(os.path.join(binpath, 'yell'), os.X_OK))
        self.assertTrue(os.access(os.path.join(binpath, 'shout'), os.X_OK))
        self.assertTrue(os.access(os.path.join(binpath, 'foo'), os.X_OK))

    def test_pot_manual(self):
        '''PO template creation with manual POTFILES.in'''

        self._mk_i18n_source()
        self._mksrc('po/foo.pot', '')
        # only do a subset here
        self._mksrc('po/POTFILES.in', '''
gtk/main.py
gui/foo.desktop.in
[type: gettext/glade]gtk/test.ui''')

        (o, e, s) = self.setup_py(['build'])
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        # POT file should not be shown as not recognized
        self.assertFalse('\n  po/foo.pot\n' in o)

        pot = self._src_contents('po/foo.pot')

        self.assertFalse('msgid "no"' in pot)
        self.assertTrue('msgid "yes1"' in pot)
        self.assertTrue('msgid "yes2 %s"' in pot)
        self.assertFalse('msgid "yes5"' in pot) # we didn't add helpers.py
        self.assertTrue('msgid "yes7"' in pot) # we did include the desktop file
        self.assertFalse('msgid "yes5"' in pot) # we didn't add helpers.py
        self.assertTrue('msgid "yes11"' in pot) # we added one GTKBuilder file
        self.assertFalse('msgid "yes12"' in pot) # ... but not the other

    def test_pot_auto(self):
        '''PO template creation with automatic POTFILES.in'''

        self._mk_i18n_source()

        (o, e, s) = self.setup_py(['build'])
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        # POT file should not be shown as not recognized
        self.assertFalse('\n  po/foo.pot\n' in o)

        pot = self._src_contents('po/foo.pot')

        self.assertFalse('msgid "no"' in pot)
        for i in range(2, 15):
            self.assertTrue('msgid "yes%i' % i in pot or 
                   'msgid ""\n"yes%i' % i in pot,
                   'yes%i' % i)
        # above loop would match yes11 to yes1 as well, so test it explicitly
        self.assertTrue('msgid "yes1"' in pot)

    def test_pot_auto_explicit(self):
        '''PO template creation with automatic POTFILES.in and explicit scripts'''

        self._mk_i18n_source()

        # add some additional binaries here which aren't caught by default
        self._mksrc('cli/client-cli', "#!/usr/bin/python\nprint (_('yes15'))", True)
        self._mksrc('gtk/client-gtk', '#!/usr/bin/python\nprint (_("yes16"))', True)
        # this is the most tricky case: intltool doesn't consider them Python
        # files by default and thus just looks for _(""):
        self._mksrc('kde/client-kde', "#!/usr/bin/python\nprint (_('yes17'))", True)
        self._mksrc('po/POTFILES.in.in', 'gtk/client-gtk\nkde/client-kde')
        self._mksrc('setup.py', '''
from DistUtilsExtra.auto import setup

import warnings
warnings.filterwarnings('ignore', 'pipe2 set errno ENOSYS.*')

setup(
    name='foo',
    version='0.1',
    data_files=[('share/foo', ['gtk/client-gtk', 'kde/client-kde'])],
    scripts=['cli/client-cli'],
)
''')

        (o, e, s) = self.setup_py(['build'])
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        # POT file should not be shown as not recognized
        self.assertFalse('\n  po/foo.pot\n' in o)

        pot = self._src_contents('po/foo.pot')

        self.assertFalse('msgid "no"' in pot)
        for i in range(2, 18):
            self.assertTrue('msgid "yes%i' % i in pot or 
                   'msgid ""\n"yes%i' % i in pot,
                   'yes%i' % i)
        # above loop would match yes11 to yes1 as well, so test it explicitly
        self.assertTrue('msgid "yes1"' in pot)

    def test_standard_files(self):
        '''Standard files (MANIFEST.in, COPYING, etc.)'''

        self._mksrc('AUTHORS')
        self._mksrc('COPYING')
        self._mksrc('LICENSE')
        self._mksrc('COPYING.LIB')
        self._mksrc('README.txt')
        self._mksrc('MANIFEST.in')
        self._mksrc('MANIFEST')
        self._mksrc('NEWS')
        self._mksrc('TODO')

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertFalse('following files are not recognized' in o, o)

        f = self.installed_files()
        self.assertTrue('/usr/share/doc/foo/README.txt' in f)
        self.assertTrue('/usr/share/doc/foo/NEWS' in f)
        ftext = '\n'.join(f)
        self.assertFalse('MANIFEST' in ftext)
        self.assertFalse('COPYING' in ftext)
        self.assertFalse('COPYING' in ftext)
        self.assertFalse('AUTHORS' in ftext)
        self.assertFalse('TODO' in ftext)

        # sub-dir READMEs shouldn't be installed by default
        self.snapshot = None
        self._mksrc('extra/README')
        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertTrue('following files are not recognized' in o)
        self.assertTrue('\n  extra/README\n' in o)

    def test_sdist(self):
        '''default MANIFEST'''

        good = ['AUTHORS', 'README.txt', 'COPYING', 'helpers.py',
                'foo/__init__.py', 'foo/bar.py', 'tests/all.py',
                'gui/x.desktop.in', 'backend/foo.policy.in',
                'daemon/backend.conf', 'x/y', 'po/de.po', 'po/foo.pot',
                '.quickly', 'data/icons/16x16/apps/foo.png', 'bin/foo',
                'backend/food', 'backend/com.example.foo.service',
                'gtk/main.glade', 'dist/extra.tar.gz']
        bad = ['po/de.mo', '.helpers.py.swp', '.bzr/index', '.svn/index',
               '.git/index', 'bin/foo~', 'backend/foo.pyc', 
               'dist/foo-0.1.tar.gz', '.shelf/1', '.bzr/revs', '.git/config']

        for f in good + bad:
            self._mksrc(f)

        (o, e, s) = self.setup_py(['sdist', '-o'])
        self.assertTrue("'MANIFEST.in' does not exist" in e)
        self.assertEqual(s, 0)

        manifest = self._src_contents('MANIFEST').splitlines()

        for f in good:
            self.assertTrue(f in manifest, '%s in manifest' % f)
        for f in bad:
            self.assertFalse(f in manifest, '%s not in manifest' % f)
        os.unlink(os.path.join(self.src, 'MANIFEST'))

    def test_ui(self):
        '''GtkBuilder/Qt *.ui'''

        self._mksrc('gtk/test.ui', b'''<?xml version="1.0"?>
<interface>
  <requires lib="gtk+" version="2.16"/>
  <object class="GtkWindow" id="window1">
    <property name="title" translatable="yes">my\xe2\x99\xa5</property>
    <child><placeholder/></child>
  </object>
</interface>'''.decode('UTF-8'))

        self._mksrc('gtk/settings.ui', '''<?xml version="1.0"?>
<!-- Generated with glade 3.18.3 -->
<interface domain="foobar">
  <requires lib="gtk+" version="2.16"/>
  <object class="GtkWindow" id="window2">
    <property name="title" translatable="yes">yes12</property>
    <child><placeholder/></child>
  </object>
</interface>''')

        self._mksrc('kde/mainwindow.ui', '''<?xml version="1.0"?>
<ui version="4.0">
 <class>CrashDialog</class>
 <widget class="QDialog" name="CrashDialog">
 </widget>
</ui>
''')

        self._mksrc('someweird.ui')

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertTrue('following files are not recognized' in o)
        self.assertTrue('\n  someweird.ui\n' in o)

        f = self.installed_files()
        self.assertTrue('/usr/share/foo/test.ui' in f)
        self.assertTrue('/usr/share/foo/settings.ui' in f)
        self.assertTrue('/usr/share/foo/mainwindow.ui' in f)
        ftext = '\n'.join(f)
        self.assertFalse('someweird' in ftext)

    def test_manpages(self):
        '''manpages'''

        self._mksrc('man/foo.1', '.TH foo 1 "Jan 01, 1900" "Joe Developer"')
        self._mksrc('daemon/food.8', '.\" some comment\n.TH food 8 "Jan 01, 1900" "Joe Developer"')
        self._mksrc('cruft/food.1', '')
        self._mksrc('daemon/notme.s', '.TH food 8 "Jan 01, 1900" "Joe Developer"')

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertTrue('following files are not recognized' in o)
        self.assertTrue('\n  cruft/food.1\n' in o)
        self.assertTrue('\n  daemon/notme.s\n' in o)

        f = self.installed_files()
        self.assertTrue('/usr/share/man/man1/foo.1' in f)
        self.assertTrue('/usr/share/man/man8/food.8' in f)
        ftext = '\n'.join(f)
        self.assertFalse('food.1' in ftext)
        self.assertFalse('notme' in ftext)

    def test_etc(self):
        '''etc/*'''

        self._mksrc('etc/cron.daily/foo')
        self._mksrc('etc/foo.conf')
        self._mksrc('etc/init.d/foo', executable=True)
        d = os.path.join(self.src, 'etc', 'cron.weekly')
        os.mkdir(d)
        os.symlink(os.path.join('..', 'cron.daily', 'foo'),
                os.path.join(d, 'foo'))

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertFalse('following files are not recognized' in o, o)

        f = self.installed_files()
        self.assertTrue('/etc/cron.daily/foo' in f)
        self.assertTrue('/etc/cron.weekly/foo' in f)
        self.assertTrue('/etc/init.d/foo' in f)
        self.assertTrue('/etc/foo.conf' in f)

        # verify that init script is executable
        self.assertTrue(os.access(os.path.join(self.install_tree, 'etc', 'init.d',
            'foo'), os.X_OK))
        # verify that symlinks get preserved
        self.assertTrue(os.path.islink(os.path.join(self.install_tree, 'etc',
            'cron.weekly', 'foo')))

        # check that we can install again into the same source tree
        (o, e, s) = self.setup_py(['install', '--no-compile', '--prefix=/usr', 
            '--root=' + self.install_tree])
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertFalse('following files are not recognized' in o, o)

    def test_requires_provides(self):
        '''automatic requires/provides'''

        for needed_pkg in ['pkg_resources','httplib2','gi.repository.GLib']:
            try:
                __import__(needed_pkg)
            except ImportError:
                self.fail('You need to have %s installed for this test suite to work' % needed_pkg)

        self._mksrc('foo/__init__.py', '')
        self._mksrc('foo/stuff.py', '''import xml.parsers.expat
import os, os.path, email.mime, distutils.command.register
from email import header as h
import httplib2.iri2uri, unknown
from . bar import poke
from bar.poke import x
import grab_cli
import broken
''')

        self._mksrc('foo/bar/__init__.py', '')
        self._mksrc('foo/bar/poke.py', 'from . import broken\ndef x(): pass')
        self._mksrc('foo/bar/broken.py', 'raise RuntimeError("cannot initialize system")')

        self._mksrc('mymod.py', 'import foo\nfrom foo.bar.poke import x')
        # trying to import this will cause setup.py to not process any args any more
        self._mksrc('grab_cli.py', 'from optparse import OptionParser\nOptionParser().parse_args()')
        # trying to import this will break setup.py
        self._mksrc('broken.py', 'raise SystemError("cannot initialize system")')
        self._mksrc('pygi.py', 'from gi.repository import GLib\nimport gi.repository.GObject')

        self._mksrc('bin/foo-cli', '''#!/usr/bin/python
import sys
import pkg_resources
import foo.bar
from httplib2 import iri2uri

print ('import iamnota.module')
''', executable=True)

        # this shouldn't be treated specially
        self._mksrc('data/example-code/template.py', 'import example.module')
        self._mksrc('data/example-code/mymod/__init__.py', '')
        self._mksrc('data/example-code/mymod/shiny.py', 'import example.othermod')

        (o, e, s) = self.do_install()
        self.assertEqual(s, 0, e)
        self.assertEqual(e, 'ERROR: Python module unknown not found\n')
        self.assertFalse('following files are not recognized' in o)

        inst = self.installed_files()
        self.assertTrue('/usr/share/foo/example-code/template.py' in inst)
        self.assertTrue('/usr/share/foo/example-code/mymod/shiny.py' in inst)
        for f in inst:
            if 'template.py' in f or 'shiny' in f:
                self.assertFalse('packages' in f)

        # parse .egg-info
        (o, e, s) = self.setup_py(['install_egg_info', '-d', self.install_tree])
        self.assertEqual(e, 'ERROR: Python module unknown not found\n')
        egg = self._installed_contents('foo-0.1.egg-info').splitlines()
        self.assertTrue('Name: foo' in egg)

        # check provides
        prov = [prop.split(' ', 1)[1] for prop in egg if prop.startswith('Provides: ')]
        self.assertEqual(set(prov), set(['foo', 'mymod', 'broken', 'grab_cli', 'pygi']))

        # check requires
        req = [prop.split(' ', 1)[1] for prop in egg if prop.startswith('Requires: ')]
        self.assertEqual(set(req), set(['httplib2', 'pkg_resources',
            'gi.repository.GLib', 'gi.repository.GObject']))

    def test_help_docbook(self):
        '''Docbook XML help'''

        self._mksrc('help/C/index.docbook')
        self._mksrc('help/C/legal.xml')
        self._mksrc('help/C/figures/mainscreen.png')
        self._mksrc('help/de/index.docbook')
        self._mksrc('help/de/legal.xml')
        self._mksrc('help/de/figures/mainscreen.png')

        self._mksrc('help/weird.xml')
        self._mksrc('help/notme.png')

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertTrue('following files are not recognized' in o)
        self.assertTrue('\n  help/weird.xml\n' in o)
        self.assertTrue('\n  help/notme.png\n' in o)

        f = self.installed_files()
        self.assertTrue('/usr/share/help/C/foo/index.docbook' in f)
        self.assertTrue('/usr/share/help/C/foo/legal.xml' in f)
        self.assertTrue('/usr/share/help/C/foo/figures/mainscreen.png' in f)
        self.assertTrue('/usr/share/help/de/foo/index.docbook' in f)
        self.assertTrue('/usr/share/help/de/foo/legal.xml' in f)
        self.assertTrue('/usr/share/help/de/foo/figures/mainscreen.png' in f)

    def test_help_mallard(self):
        '''Mallard XML help'''

        self._mksrc('help/C/index.page')
        self._mksrc('help/C/legal.page')
        self._mksrc('help/C/figures/mainscreen.png')
        self._mksrc('help/de/index.page')
        self._mksrc('help/de/legal.page')
        self._mksrc('help/de/figures/mainscreen.png')

        self._mksrc('help/weird.page')
        self._mksrc('help/notme.png')

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertTrue('following files are not recognized' in o)
        self.assertTrue('\n  help/weird.page\n' in o)
        self.assertTrue('\n  help/notme.png\n' in o)

        f = self.installed_files()
        self.assertTrue('/usr/share/help/C/foo/index.page' in f)
        self.assertTrue('/usr/share/help/C/foo/legal.page' in f)
        self.assertTrue('/usr/share/help/C/foo/figures/mainscreen.png' in f)
        self.assertTrue('/usr/share/help/de/foo/index.page' in f)
        self.assertTrue('/usr/share/help/de/foo/legal.page' in f)
        self.assertTrue('/usr/share/help/de/foo/figures/mainscreen.png' in f)

    def test_binary_files(self):
        '''Binary files are ignored'''

        with open(os.path.join(self.src, 'binary_trap'), 'wb') as f:
            f.write(b'\x00\x01abc\xFF\xFE')
        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)
        self.assertTrue('following files are not recognized' in o, o)
        self.assertTrue('\n  binary_trap\n' in o)

        f = self.installed_files()
        self.assertEqual(len(f), 1, f)
        self.assertTrue('egg-info' in f[0])

    def test_utf8_filenames(self):
        '''UTF-8 file names'''
            
        bin_fname = b'a\xc3\xa4b.bin'.decode('UTF-8')
        with open(os.path.join(self.src, bin_fname).encode('UTF-8'), 'wb') as f:
            f.write(b'\x00\x01abc\xFF\xFE')

        (o, e, s) = self.do_install()
        self.assertEqual(e, '')
        self.assertEqual(s, 0)

        f = self.installed_files()
        self.assertEqual(len(f), 1, f)
        self.assertTrue('egg-info' in f[0])

        self.assertTrue('following files are not recognized' in o)
        # this might not be the correct file name when the locale is e. g. C
        self.assertTrue('b.bin\n' in o, o)

    #
    # helper methods
    #

    def setup_py(self, args):
        '''Run setup.py with given arguments.

        For convenience, this snapshots the tree if no snapshot exists yet.

        Return (out, err, exitcode) triple.
        '''
        if not self.snapshot:
            self.do_snapshot()

        env = os.environ.copy()
        oldcwd = os.getcwd()
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = oldcwd + os.pathsep + env['PYTHONPATH']
        else:
            env['PYTHONPATH'] = oldcwd
        os.chdir(self.src)
        s = subprocess.Popen(['/proc/self/exe', 'setup.py'] + args, env=env,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = s.communicate()
        out = out.decode()
        err = err.decode()
        os.chdir(oldcwd)

        return (out, err, s.returncode)

    def do_install(self):
        '''Run setup.py install into temporary tree.

        Return (out, err, exitcode) triple.
        '''
        self.install_tree = tempfile.mkdtemp()

        return self.setup_py(['install', '--no-compile', '--prefix=/usr', 
            '--root=' + self.install_tree])

    def installed_files(self):
        '''Return list of file paths in install tree.'''

        result = []
        for root, _, files in os.walk(self.install_tree):
            assert root.startswith(self.install_tree)
            r = root[len(self.install_tree):]
            for f in files:
                result.append(os.path.join(r, f))
        return result

    def _mksrc(self, path, content=None, executable=False):
        '''Create a file in the test source tree.'''

        path = os.path.join(self.src, path)
        dir = os.path.dirname(path)
        if not os.path.isdir(dir):
            os.makedirs(dir)
        with open(path, 'wb') as f:
            if content is None:
                # default content, to spot with diff
                f.write(b'dummy')
            else:
                f.write((content + '\n').encode('UTF-8'))

        if executable:
            os.chmod(path, 0o755)

    def do_snapshot(self):
        '''Snapshot source tree.

        This should be called after a test set up all source files.
        '''
        assert self.snapshot is None, 'snapshot already taken'

        self.snapshot = tempfile.mkdtemp()
        shutil.copytree(self.src, os.path.join(self.snapshot, 's'), symlinks=True)

    def diff_snapshot(self):
        '''Compare source tree to snapshot.

        Return diff -Nur output.
        '''
        assert self.snapshot, 'no snapshot taken'
        diff = subprocess.Popen(['diff', '-x', 'foo.pot', '-x', '*.pyc',
            '-Nur', os.path.join(self.snapshot, 's'), self.src],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = diff.communicate()
        out = out.decode('UTF-8')
        return out

    def _mkpo(self):
        '''Create some example po files.'''

        self._mksrc('po/POTFILES.in', '')
        self._mksrc('po/de.po', '''msgid ""
msgstr "Content-Type: text/plain; charset=UTF-8\\n"

msgid "Good morning"
msgstr "Guten Morgen"

msgid "Hello"
msgstr "Hallo"''')
        self._mksrc('po/fr.po', '''msgid ""
msgstr "Content-Type: text/plain; charset=UTF-8\\n"
        
msgid "Good morning"
msgstr "Bonjour"''')

    def _mk_i18n_source(self):
        '''Create some example source files with gettext calls'''

        self._mksrc('gtk/main.py', '''print (_("yes1"))
print ("no1")
print (__("no2"))
x = _('yes2 %s') % y

def f():
    print (_("yes3"))
    return _('yes6')''')

        self._mksrc('helpers.py', '''
print (f(_("yes4")))
print (_(\'\'\'yes5
even more
lines\'\'\'))
print (_("""yes6
more lines"""))
print (\'\'\'no3
boo\'\'\')
print ("""no4
more""")''')

        self._mksrc('gui/foo.desktop.in', '''[Desktop Entry]
_Name=yes7
_Comment=yes8
Icon=no5
Exec=/usr/bin/foo''')

        self._mksrc('daemon/com.example.foo.policy.in', '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
 "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/PolicyKit/1.0/policyconfig.dtd">
<policyconfig>
  <action id="com.example.foo.greet">
    <_description>yes9</_description>
    <_message>yes10</_message>
    <defaults>
      <allow_active>no6</allow_active>
    </defaults>
  </action>
</policyconfig>''')

        self._mksrc('gtk/test.ui', '''<?xml version="1.0"?>
<interface>
  <requires lib="gtk+" version="2.16"/>
  <object class="GtkWindow" id="window1">
    <property name="title" translatable="yes">yes11</property>
    <child><placeholder/></child>
  </object>
</interface>''')

        self._mksrc('data/settings.ui', '''<?xml version="1.0"?>
<interface domain="foobar">
  <requires lib="gtk+" version="2.16"/>
  <object class="GtkWindow" id="window1">
    <property name="title" translatable="yes">yes12</property>
    <child><placeholder/></child>
  </object>
</interface>''')

        self._mksrc('Makefile', 'echo _("no7")')

        # Executables without *.py extension
        self._mksrc('gtk/foo-gtk', '#!/usr/bin/python\nprint (_("yes13"))',
                executable=True)
        self._mksrc('cli/foo-cli', '#!/usr/bin/env python\nprint (_(\'yes14\'))',
                executable=True)
        self._mksrc('daemon/foobarize', '#!/usr/bin/flex\np _("no8")',
                executable=True)

    def _src_contents(self, path):
        f = open(os.path.join(self.src, path))
        contents = f.read()
        f.close()
        return contents

    def _installed_contents(self, path):
        f = open(os.path.join(self.install_tree, path))
        contents = f.read()
        f.close()
        return contents

unittest.main()
