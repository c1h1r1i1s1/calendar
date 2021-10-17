# Contributor: Christian Fane <cfan9019@uni.sydney.edu.au>
# Maintainer: Christian Fane <cfan9019@uni.sydney.edu.au>
pkgname="py3-calendar"
pkgver="1"
pkgrel=0
pkgdesc="Retry of Assignment 2"
url="https://github.com/c1h1r1i1s1/calendar"
arch="all"
license="license.txt"
depends="python3"
makedepends="python3-dev"
install=""
subpackages=""
source="https://downloads.sourceforge.net/project/py3-calendar/calendar2.tar.gz"
builddir="$srcdir"/"$_pkgname"-"$pkgver"

build() {
	python3 "$srcdir"/setup.py build "$srcdir"
}

check() {
	python3 "$srcdir"/setup.py test "$srcdir"
}

package() {
	cd "$srcdir"
	sudo chmod +x daemon.py
	sudo chmod +x calendar.py
	sudo install -m755 -D "$srcdir"/cald  \
	/etc/init.d/cald
	cd /etc/init.d/
	sudo chmod +x cald
	sudo rc-update add cald default
	sudo ./cald start
	cd "$srcdir"
	cd ../
	cp src/calendar.py calendar.py
}

sha512sums="29a8507c9f825bef6e421605399c1a2f04c99ba57d60df0fce5a53194ed2ec0d2187b8e364ac91228b81bfced8b5686f9afd640744a196491dbb96668bed03f1  calendar2.tar.gz"
