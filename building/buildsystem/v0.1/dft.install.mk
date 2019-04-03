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
# Copyright 2017 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Even if this work is a complete rewrite, it is originally derivated work based
# upon mGAR build system from OpenCSW project (http://www.opencsw.org).
#
# Copyright 2001 Nick Moffitt: GAR ports system
# Copyright 2006 Cory Omand: Scripts and add-on make modules, except where otherwise noted.
# Copyright 2008 Dagobert Michelsen (OpenCSW): Enhancements to the CSW GAR system
# Copyright 2008-2013 Open Community Software Association: Packaging content
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

# ------------------------------------------------------------------------------
#
# Execute the install target script
#

do-install :
	if test -f $(COOKIE_DIR)/do-install ; then \
		true ; \
	else \
		echo "        running install in $(OBJ_DIR)"  ; \
	 	if [ ! "" = "$(UBOOT_VERSION)" ] ; then \
			mkdir -p $(abspath $(INSTALL_DIR))/u-boot/ ; \
			mkdir -p $(INSTALL_DIR)/doc ; \
			cp files/* $(INSTALL_DIR)/doc ; \
			cd $(abspath $(OBJ_DIR)) ; \
			cp -fr $(UBOOT_BINARY_FILE) $(abspath $(INSTALL_DIR))/u-boot/u-boot-$(BOARD_NAME)-$(UBOOT_VERSION) ; \
			cp -fr u-boot.dtb $(abspath $(INSTALL_DIR))/u-boot/u-boot-$(BOARD_NAME)-$(UBOOT_VERSION).dtb ; \
			cd $(abspath $(INSTALL_DIR))/u-boot/ ; \
			ln -sf u-boot-$(BOARD_NAME)-$(UBOOT_VERSION) u-boot-$(BOARD_NAME); \
	 	else \
			echo "        running install in $(OBJ_DIR)"  ; \
			echo "        BOARD ARCH is $(BOARD_ARCH)"  ; \
			echo "        CPU ARCH is $(CPU_ARCH)"  ; \
			mkdir -p $(abspath $(INSTALL_DIR))/boot/dtb ; \
			cd $(abspath $(OBJ_DIR)) ; \
			$(BUILD_ENV) $(MAKE) INSTALL_PATH=$(abspath $(INSTALL_DIR))/boot $(INSTALL_ARGS) ; \
			$(BUILD_ENV) $(MAKE) INSTALL_MOD_PATH=$(abspath $(INSTALL_DIR))/ INSTALL_MOD_STRIP=1 modules_install ; \
			cp -fr arch/$(CPU_ARCH)/boot/dts/*.dtb $(abspath $(INSTALL_DIR))/boot/dtb ; \
	 	    if [ ! "" = "$(DEFAULT_DTB)" ] ; then \
			    cd $(abspath $(INSTALL_DIR)/boot) ; \
			    ln -sf dtb/$(DEFAULT_DTB) default.dtb ; \
		    fi ; \
		fi ; \
	fi ;
	@$(TARGET_DONE)

do-reinstall :
	@if test -f $(COOKIE_DIR)/do-install ; then \
		rm -f $(COOKIE_DIR)/do-install ; \
		rm -fr $(abspath $(INSTALL_DIR)) ; \
	fi ;
	$(TARGET_DONE)





le do installl est fau
 DEPMOD  5.0.3
make[1]: Leaving directory '/media/william/132c8116-ac9b-49b0-b626-85714ec13422/work/dft/building/kernel/pinebook/5.0.3/work-pinebook/build-pinebook/linux-5.0.3'
cp: cannot stat 'arch/aarch64/boot/dts/*.dtb': No such file or directory
    completed [install] 
    completed [reinstall] 
(william@pinebook):5.0.3$ ls /media/william/132c8116-ac9b-49b0-b626-85714ec13422/work/dft/building/kernel/pinebook/5.0.3/work-pinebook/build-pinebook/linux-5.0.3
arch        certs    crypto         firmware  init    Kconfig  LICENSES     mm               Module.symvers  samples   sound       usr      vmlinux.o
block       COPYING  Documentation  fs        ipc     kernel   MAINTAINERS  modules.builtin  net             scripts   System.map  virt
built-in.a  CREDITS  drivers        include   Kbuild  lib      Makefile     modules.order    README          security  tools       vmlinux
(william@pinebook):5.0.3$ ls /media/william/132c8116-ac9b-49b0-b626-85714ec13422/work/dft/building/kernel/pinebook/5.0.3/work-pinebook/build-pinebook/linux-5.0.3/arch/
alpha  arm    c6x   h8300    ia64     m68k        mips   nios2     parisc   riscv  sh     um         x86
arc    arm64  csky  hexagon  Kconfig  microblaze  nds32  openrisc  powerpc  s390   sparc  unicore32  xtensa
(william@pinebook):5.0.3$ ls /media/william/132c8116-ac9b-49b0-b626-85714ec13422/work/dft/building/kernel/pinebook/5.0.3/work-pinebook/build-pinebook/linux-5.0.3/arch/armboot           kvm           mach-berlin     mach-footbridge  mach-keystone  mach-mxs        mach-prima2    mach-sa1100    mach-uniphier   net             tools
common         lib           mach-clps711x   mach-gemini      mach-ks8695    mach-netx       mach-pxa       mach-shmobile  mach-ux500      nwfpe           vdso
configs        mach-actions  mach-cns3xxx    mach-highbank    mach-lpc18xx   mach-nomadik    mach-qcom      mach-socfpga   mach-versatile  oprofile        vfp
crypto         mach-alpine   mach-davinci    mach-hisi        mach-lpc32xx   mach-npcm       mach-rda       mach-spear     mach-vexpress   plat-iop        xen
firmware       mach-artpec   mach-digicolor  mach-imx         mach-mediatek  mach-nspire     mach-realview  mach-sti       mach-vt8500     plat-omap
include        mach-asm9260  mach-dove       mach-integrator  mach-meson     mach-omap1      mach-rockchip  mach-stm32     mach-w90x900    plat-orion
Kconfig        mach-aspeed   mach-ebsa110    mach-iop13xx     mach-mmp       mach-omap2      mach-rpc       mach-sunxi     mach-zx         plat-pxa
Kconfig.debug  mach-at91     mach-efm32      mach-iop32x      mach-moxart    mach-orion5x    mach-s3c24xx   mach-tango     mach-zynq       plat-samsung
Kconfig-nommu  mach-axxia    mach-ep93xx     mach-iop33x      mach-mv78xx0   mach-oxnas      mach-s3c64xx   mach-tegra     Makefile        plat-versatile
kernel         mach-bcm      mach-exynos     mach-ixp4xx      mach-mvebu     mach-picoxcell  mach-s5pv210   mach-u300      mm              probes
(william@pinebook):5.0.3$ ls /media/william/132c8116-ac9b-49b0-b626-85714ec13422/work/dft/building/kernel/pinebook/5.0.3/work-pinebook/build-pinebook/linux-5.0.3/arch/arm64/
boot  configs  crypto  include  Kconfig  Kconfig.debug  Kconfig.platforms  kernel  kvm  lib  Makefile  mm  net  xen
(william@pinebook):5.0.3$ ls /media/william/132c8116-ac9b-49b0-b626-85714ec13422/work/dft/building/kernel/pinebook/5.0.3/work-pinebook/build-pinebook/linux-5.0.3/arch/arm64/boot/
dts  Image  Image.gz  install.sh  Makefile




tu melange linstall des dtb et du noyau ce sont deux trucs different reprend calmement en regrdant ce que le pinbook a d install dans / boo et procede par analogie


