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
# Copyright 2016 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

#
# Target : init
#
# Description :
#
#	Install all requirements using PIP
#
init:
	pip3 install -r requirements.txt

#
# Target : test, tests
#
# Description :
#
#	Run unit tests
#
tests: test

test:
	nosetests

#
# Target : deb-package
#
# Description :
#
#	Build the debian packages using debuild
#
deb-package:
	pwd ; \
	ls -l .. \
	rm -f ../dft_`grep ^dft debian/changelog | head -n 1 | tr \( \  | tr \) \ | tr - \ | awk ' { print $$2 } '`.orig.tar.gz ; \
	tar cvfz ../dft_`grep ^dft debian/changelog | head -n 1 | tr \( \  | tr \) \ | tr - \ | awk ' { print $$2 } '`.orig.tar.gz * ; \
	debuild -us -uc -ui ; 

#
# Target : publish_dft_pkg_to_armwizard_repo
#
# Description :
#
#	Build if needed the debian packages using debuild and push them to armwizard repository incoming folder
#
publish_dft_armwizard: deb-package
	scp ../dft_*.{deb,build,buildinfo,changes,tar.xz,dsc} ${ARMWIZARD_REPO_USER}@${ARMWIZARD_WEBSERVER}:${DFT_REMOTE_REPO_INCOMING_PATH}/
