#BSP Packages
This folder contains the makefiles used to compile and build BSP (Board Support Packages) from upstream sources, a local mirror or even modified/patched sources, handling both Linux kernel and u-boot.

The produced Debian ***deb*** packages can be installed to your own system and can also be used by the DFT command line tool when producing a bootable image.

The Firmware toolkit project contributes the build manifests you need to rebuild the BSP from sources, using either provided configuration files, or your own tuned defconfigs. This feature is compliant with the tracking of used defconfigs and configure options in your own SCM system (such as git). It also covers needs such as, tuning the kernel, enable specific options or drivers to reduce the footprint by switching drivers from module to static mode etc.

The bsp-packages directory tree is organized in the same way as others top level directories containing a board ***category*** level.

* The following categories are availables :
  * desktop
  * laptop
  * single-board-computer (*SBC*)
  * set-top-box (*STB*)

The category folders contain sublevel folders, one per board in the given category.
All the board folders have the same structure, even if hardware architecture differ.
Board folders contain a kernel and a u-boot subfolder, if u-boot is supported by hardware otherwise grub can be used.

Linux kernel and u-boot folders contain a separate subdirectory per supported kernel and u-boot version.

This tree structure is consistent for all the board categories, whatever architecture or manufacturer are. Providing a standardized interface and Makefile driven interface to build and packages sofware components.

##Makefile targets
The following targets are available to help you run the most common tasks.
###u-boot-package
This target is recursivly called in categories subfolders in order to build u-boot packages for every board in the current category (if u-boot is supported by the board).
###linux-kernel-package
This target is recursivly called in categories subfolders in order to build kernel packages for every board in the current category. This target does not compile u-boot, if you need to produce both kernel and u-boot at the same time with a single make commande please use make bsp-package.

You can also use the target ***kernel-package*** as a synonym, since only linux kernel is supported.
###bsp-package
This target is recursivly called in categories subfolders in order to build all the Board Support Packages for every board in the current category, including both kerl and u-boot (if u-boot is supported by the board).

You can also use the target ***bsp*** as a synonym.


