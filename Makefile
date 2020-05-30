# vim: ft=make ts=4 sw=4 noet
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
# Copyright 2019 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#

# Build system sould be available from the root of git clone.
DFT_BUILDSYSTEM := ./buildsystem

# Do not recurse the following subdirs
MAKE_FILTERS  = Makefile README.md .

# Definition of the folders to check for sanity
CHECK_FOR_SANITY    = ansible-roles bsp-packages board-images

# ------------------------------------------------------------------------------
#
# Targets not associated with a file (aka PHONY)
#
.PHONY: help sanity-check

# Simple forwarder
sanity-check:
	@for i in $(CHECK_FOR_SANITY) ; do \
		if [ -f ${CURDIR}/$$i/Makefile ] ; then \
			$(MAKE) -C $$i $@ ; \
		fi ; \
	done

# Forward list-boards to bsp-packages folder
list-boards list-architectures :
	@$(MAKE) --no-print-directory -C bsp-packages $@ arch=$(arch) category=$(category); \

# ------------------------------------------------------------------------------
#
# Target that prints the generic top level help
#
help:
	@echo "Inline help is allocated in several sections according to covered functionnal scope"
	@echo 
	@echo "Available targets to display scoped help are :"
	@echo " help-bsp                Help about BSP building targets"
	@echo " help-config-file        Help about configuration file"
	@echo " help-env-vars           Help about environnment variables"
	@echo " help-catalog            Help about catalog listing target (list of supported board, arch, versions)"
	@echo " help-images             Help about image building targets"
	@echo " help-examples           Help about examples building targets"
	@echo " help-sanity             Help about buildsystem sanity check targets"
	@echo " help                    Display this help"

# ------------------------------------------------------------------------------
#
# Help about images building targets
#
help-images:
	@echo "Board image management functionalities. The following helper targets can be used to query"
	@echo "and modify the catalog of board images  (such as adding new images for a board)"
	@echo
	@echo "Available targets are :"
	@echo "    list-images             Display the list of avalable images (accept filters)"
	@echo
	@echo "Available filters for the list targets are :"
	@echo "    mode=                   (supported values are rootfs and firmware)"
	@echo "    flavor=                 (project flavor used to build the image ex:netshell,xenhv)"
	@echo
	@echo "One or several filters can be passed to the make command to reduce the ouput of list-* targets"

# ------------------------------------------------------------------------------
#
# Help about bsp building targets
#
help-bsp:
	@echo "Board Support Packages management functionalities. The following helper targets can be used to ..."
	@echo
	@echo "At board level, or upper, available targets are :"
	@echo "    kernel-package         Recursivly build all versions of Linux kernel packages (accept filters)"
	@echo "    u-boot-package         Recursivly build all versions of u-boot packages (accept filters)"
	@echo
	@echo "At sofware level (kernel or u-boot) available targets are :"
	@echo "    build                  Build contexte software from sources"
	@echo "    checksum               Compare the checksums of downloaded files to the content of checksums file"
	@echo "    configure              Execute the configure script from extracted sources"
	@echo "    install                Install the software to the target directory under workdir"
	@echo "    extract                Extract the content of the files downloaded by fetch target"
	@echo "    fetch                  Download software sources from upstream site"
	@echo "    fetch-list             Show the list of files that would be retrieved by fetch"
	@echo "    makesum(s)             Compute the checksums and create the checksum file"
	@echo "    patch                  Apply the patches identified by the PATCHFILES variable if defined in Makefile"
	@echo " XXX Todo add filters in help"
	@echo "                            then into all its subfolders (sub makefiles have"
	@echo "                            to support the clean target or an arror will occur)"
	@echo "    show-config            Display the build system configuration and internal variables"
	@echo
	@echo "    mrproper               Destroy the target (target context only) work directory and cookies."
	@echo "                           Thus every steps done for this target will have to be executed again"
	@echo "                           since there will be nothing left in this context work directory."
	@echo "                           Sources will be (re)downloaded then extracted, compiled, etc."
	@echo "                           It may last very longtime. Perhaps, you should use a re-target instead ?"
	@echo "                           "
	@echo "                           Warning !!! You will also loose all the local modifications you could have done !!!"
	@echo "                           You have been warned :)"
	@echo "                           "
	@echo "   bsp[-package] | package Build all versions of BSP software packages (both linux kernel and u-boot)"
	@echo "   u-boot-package          Build all versions of u-boot package (and only u-boot, thus no kernel)"
	@echo "                           for board $(BOARD_NAME)"
	@echo "   sanity-check            Verify the availability of required items (files, symlinks, directories)"
	@echo "   re[target]              Force execution of [target] even if already done (without re-executing dependencies)"
	@echo "                           "
	@echo "                           All targets are recursive. It means that make will walk down through the whole tree."
	@echo "                           Iterating categories, then boards, softwares, every versions and finally call the"
	@echo "                           given target in current location. Recursive target execution is handy but it can"
	@echo "                           use a lot of time, cpu and network bandwidth."
	@echo "                           "
	@echo "                           Please note that during tree walk if host and target architectures are different make"
	@echo "                           will NOT execute configure, install nor build targets. Host is the machine you use to"
	@echo "                           run make command and target is the machine you are building for."
	@echo "                           "
	@echo "                           Since cross compilation is not supported, to build binaries for different arch"
	@echo "                           you need at least one builder per arch and to collect generated .deb files"
	@echo "                           "
	@echo "   help                    Display this help"
	@echo "   help-config             Display help about global environment and configuration variables"
	@echo "                           "
	@echo "                           "
	@echo "                           While recursively walking the tree of category and board, make encounters targets using"
	@echo "                           a CPU architecture different from the one make and build toolchain are running on."
	@echo "                           The following command line variables can be used to control make behavior when dealing"
	@echo "                           with arch dependant targets:"
	@echo "                           "
	@echo "                           arch-warning=0     (display warning when skipping a target because of arch"
	@echo "                                               compatibility. default value=0)"
	@echo "                           only-native-arch=1 (skip all targets, it means no dowload nor extract, if builder"
	@echo "                                               arch is different from target board arch. You need a distinct"
	@echo "                                               builder per hardware arch. default value=0)"
	@echo "                           "
	@echo "   The following targets are recursive and available only if write access to buildsystem is granted. New files"
	@echo "   and folders will be created under buildsystem during execution. New items will not be added automatically to git."
	@echo "   git add has to be done manually, depending on you workspace, as the pull request if needed by the git server."
	@echo "                           "
	@echo "    add-u-boot-version      new-version=YYYY.MM (require write acess)"
	@echo "                            Create a new supported u-boot version entry. ex: make add-u-boot-version new-version=2019.07"
	@echo "                            This target will create a subdirectory named after the content of the new-version variable."
	@echo "                            It will contain the Makefile and all the files needed to fetch and build the given"
	@echo "                            version. It also instanciate Debian package template."
	@echo "                           "
	@echo "    check-u-boot-defconfig  Check defconfig target availability from upstream sources"


# ------------------------------------------------------------------------------
#
# Help about configuration file
#
help-config-file:
	@echo "Displays variables from defined in used dftrc configuration"
	@echo
	@echo "Available targets are :"
	@echo "    list-config-vars        List variables which can be defined in configuration file"
	@echo "    show-config-file        Display the path to the config file used by the build system"
	@echo "    show-config-vars        Display the values oof variables defined in config file"

# ------------------------------------------------------------------------------
#
# Help about configuration file
#
help-env-vars:
	@echo "Displays variables defined in dftrc configuration file"
	@echo
	@echo "Available targets are :"
	@echo "    list-env-vars           List variables which can be defined in shell environment"
	@echo "    show-env-vars           Display the values of the variables as defined in shell environment"

# ------------------------------------------------------------------------------
#
# Help about buildsystem sanity check targets
#
help-sanity:
	@echo "Available targets are :"
	@echo "    sanity-check            Recursivly check subdirs for missing required items (files, symlinks, directories)"
	@echo "                            This target only warns you and propose fixes, it makes no change to the tree content."
	@echo "    check-u-boot-defconfig  Check defconfig target availability from upstream sources"


# ------------------------------------------------------------------------------
#
# Help about examples building targets
#
help-examples:
	@echo "Example project management functionalities. The following helper targets XXX TODO"
	@echo
	@echo "Available targets are :"
	@echo "    list-xxx                XXX"

# ------------------------------------------------------------------------------
#
# Help about targets handling catalog of supported items printing and querying
#
help-catalog:
	@echo "Catalog management functionalities. The following helper targets can be used to query"
	@echo "and modify the catalog (such as adding new boards or categories)"
	@echo
	@echo "Available targets are :"
	@echo "    list-boards             Display the list of supported boards (accept filters)"
	@echo "    list-architectures      Display the list of supported CPU architectures (accept filters)"
	@echo
	@echo "Available filters for the list targets are :"
	@echo "    arch=                   (supported values are return values of command uname --machine)"
	@echo "    category=               (desktop laptop phone set-top-box single-board-computer tablet)"
	@echo
	@echo "One or several filters can be passed to the make command to reduce the ouput of list-* targets"

