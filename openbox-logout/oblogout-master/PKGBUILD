#Contributor : Andrew Williams <andy@tensixtyone.com.com>
pkgname=oblogout
pkgver=0.3
pkgrel=1
pkgdesc="OBLogout is a expandable, configurable, and theme-able logout script designed to be used in a Openbox desktop environment."
url="http://launchpad.net/oblogout/"
license=("GPL2")
arch=('i686' 'x86_64')
depends=('python>=2.5' 'dbus-python' 'pil' 'pygtk' )
makedepends=('bzr setuptools python-distutils-extra')
optdepends=('dbus-python' 'policykit' 'policykit-gnome' 'policykit-kde')
provides=('oblogout')
conflicts=('oblogout')

_bzrbranch=http://bazaar.launchpad.net/~nikdoof/oblogout/0.3/

build() {
  cd ${srcdir}

  if [ -d .bzr ]; then
    bzr pull
  else
    bzr branch $_bzrbranch $pkgname 
  fi

  msg "Bzr clone done or server timeout"

  cd $pkgname
  python setup.py install --root=$startdir/pkg

}

