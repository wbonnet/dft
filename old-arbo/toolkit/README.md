dft
====

Debian Firmware Toolkit is an Experimentation project with LFS and Debian to build squashfs firmware targetting Raspberry PI, Beagle board and x86 VMs. 

It was originnaly named Linux Firmware From Scratch


Build System description
========================

The DFT build system is in buildsystem subdirectory. The following commands are available, and are described hereafter :

* assemble_firmware
* build_bootloader
* build_firmware
* build_image
* build_rootfs
* check_rootfs
* factory_setup
* generate_content_information
* strip_rootfs

assemble_firmware
-----------------

build_bootloader
----------------

build_firmware
--------------

build_image
-----------

build_rootfs
------------

check_rootfs
------------

factory_setup
-------------

generate_content_information
----------------------------

strip_rootfs
------------






Depot
	=> mirroring
	=> population locale


Construction RootFS						=> build_rootfs
	<= depot
	=> base
	=> modulation

Construction du firmware  				=> build_firmware
	xxx

Chaine de build_rootfs					=> build_bootloader
	<= sources ?
	=> noyau
	=> uboot


xxx config usine						=> factory_setup
xxx creation squashfs					=> assemble ?
xxx striping							=> strip_rootfs
xxx Assemblage du firmware				=> assemble_firmware
xxx outils de controles secu etc
xxx generation image carte				=> build_image










