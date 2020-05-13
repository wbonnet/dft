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
# Target : publish_dft_to_repo
#
# Description :
#
#	Build if needed the debian packages using debuild then push to repository repository incoming folder
#
publish_dft_to_repo:
	@if [ ! "" = "$(DFT_DEB_UPLOAD_PATH)" ] && [ ! "" = "$(DFT_DEB_UPLOAD_USER)" ] && [ ! "" = "$(DFT_DEB_UPLOAD_SERVER)" ] ; then \
		scp $$COPY_LIST $(DFT_DEB_UPLOAD_USER)@$(DFT_DEB_UPLOAD_SERVER):$(DFT_DEB_UPLOAD_PATH) ; \
	else \
		if [ "" = "$(DFT_DEB_UPLOAD_SERVER)" ] ; then \
		    echo "        Variable DFT_DEB_UPLOAD_SERVER is not set, please define it your shell environment." ; \
		else \
	    	echo "        DFT_DEB_UPLOAD_SERVER = $(DFT_DEB_UPLOAD_SERVER)."  ; \
		fi ; \
		if [ "" = "$(DFT_DEB_UPLOAD_USER)" ] ; then \
		    echo "        Variable DFT_DEB_UPLOAD_USER is not set, please define it your shell environment." ; \
		else \
	    	echo "        DFT_DEB_UPLOAD_USER = $(DFT_DEB_UPLOAD_USER)."  ; \
		fi ; \
		if [ "" = "$(DFT_DEB_UPLOAD_PATH)" ] ; then \
	    	echo "        Variable DFT_DEB_UPLOAD_PATH is not set, please define it your shell environment." ; \
		else \
	    	echo "        DFT_DEB_UPLOAD_PATH = $(DFT_DEB_UPLOAD_PATH)"  ; \
		fi ; \
	fi ; \
	scp $$COPY_LIST ${DFT_DEB_UPLOAD_USER}@${DFT_DEB_UPLOAD_SERVER}:${DFT_DEB_UPLOAD_PATH} ; \
