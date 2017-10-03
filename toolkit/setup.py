#
# The contents of this file are subject to the Apache 2.0 license you may not
# use this file except in compliance with the License.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
#
# Copyright 2016 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
# Debian Firmware Toolkit is the new name of Linux Firmware From Scratch
# Copyright 2014 LFFS project (http://www.linuxfirmwarefromscratch.org).
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

from dft.release import __version__, __author__, __author_email__

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

config = {
    'description': 'Debian Firmware Toolkit',
    'long_description': 'DFT is a firmware used to produce firmware from a standard Debian repositories',
    'author': __author__,
    'url': 'https://github.com/wbonnet/dft/',
    'download_url': 'https://github.com/wbonnet/dft/',
    'author_email': __author_email__,
    'version': __version__,
    'install_requires': [ 'pyyaml', 'pyparted' ],
    'packages': ['dft'],
    'scripts': [ 'bin/dft' ],
    'name': 'dft'
}

setup(**config)

