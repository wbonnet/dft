# Linux Kernel configuration fragments
The folder linux-kernel-fragments contains the Linux kernel configuration fragments provided with Firmware Toolkit.

These defconfig fragments are available in order to rebuild kernels or can be used as examples, to configure then build
your own customized kernel.

Fragments are stored in two distinct sublfolders according to the nature of provided features. Either hardware or kernel functionality support.

Features are assigned to independant axis ***functional *** and ***hardware *** axis (stored in subfolders). This let you select enabled or not features on a given hardware.

On both axis, features are grouped into folders by function type. Each set of functionality is defined into a distinct file that should be included, at compilation time, from kernel Makefile (please see documantation and howto from in the Makefile section).

* The ***functional*** features are grouped into the following categories (or subfolders):
  * containers (which activate cgroups and namespaces, virtualization is below)
  * crypto (cryptography support)
  * debug (kernel debug and trace support)
  * filesystems (supported filesystems)
  * network (network features support)
  * security (security support)
  * virtualization (virtualization support)

* The ***hardware*** features axis
  * board blueprints (board and architectures specific features)
  * device drivers (device support which can be reused by distinct boards)
