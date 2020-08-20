# Board support resources
The folder board-support contains the resources (build descriptions, configuration files, Makefiles, ...) needed to produce the binaries used to support boards (kernel, u-boot, etc.)

Board definitions are allocated into category folders (single-board-computer, laptop, etc.). Category folders contain sublevel folders, one per board in the given category.

Linux kernel and u-boot folders contain a separate subdirectory per supported version.

This tree structure is consistent for all the board categories, whatever are architecture or manufacturer. Providing a standardized interface and Makefile driven interface to build and packages sofware components.

The board support resources include materials needed for production of both ***BSP*** itself and generation of the bootable images using this BSP for supported boards.

All the board folders use the same directory layout. For instance, board folders contain a kernel and a u-boot subfolder, if u-boot is supported by hardware.

Binaries production is Makefile driven. Make command is in charge of making calls to the dedicated build tools and synchronize tools execution.
This allow users to execute the build steps by hand, replay process and customize execution.

The build and packaging process is controled by a configuration file named bsp-***boardname***.mk written with Makefile syntax. This file defines parameters and how to ***BSP*** packages (in Makefile syntax).

The directory tree is organized with ***category*** level folder contaning a distinct folder for each board assigne to this category.

* The following categories are availables :
  * desktop
  * devkit (*Development Kit*)
  * laptop
  * phone
  * set-top-box (*STB*)
  * single-board-computer (*SBC*)
  * tablet

The folder named *linux-kernel-fragments* contains the kernel configuration fragments shared among categories and boards.

The folder named *sbit* contains the unit tests used to validate board support by rootfs board specific images. These test suites are  defined in unit test description files and target the validation of kernel and BSP installation for a given board. Checks are done to verify kernel features activation, drivers availability, hardware and network support, etc.

These tests are operating level system level tests and hardware dependent tests. Thus there exist one test suite per distinct board. Software level tests are available from the sbit folder in board-images. Software level tests are hardware independent tests. There exist one test suite per on image flavor.

Testing a board requires to successfuly execute both hardware and software tests. Even if software tests are succesfull they should not been considered as successful as long as hardware haven't been also executed successfully as a prerequiste. 

The board image definitions are in a separate folder at the same level as this folder. Images use board-support resources in their build definition.

## Makefile targets
The following targets are available to help you run the most common tasks.
### u-boot-package
This target is recursivly called in categories subfolders in order to build u-boot packages for every board in the current category (if u-boot is supported by the board).
### linux-kernel-package
This target is recursivly called in categories subfolders in order to build kernel packages for every board in the current category. This target does not compile u-boot, if you need to produce both kernel and u-boot at the same time with a single make commande please use make bsp-package.

You can also use the target ***kernel-package*** as a synonym, since only linux kernel is supported.
### bsp-package
This target is recursivly called in categories subfolders in order to build all the Board Support Packages for every board in the current category, including both kerl and u-boot (if u-boot is supported by the board).

You can also use the target ***bsp*** as a synonym.
