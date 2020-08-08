# Linux Kernel configuration fragments
The folder linux-kernel-fragments contains the Linux kernel configuration fragments provided with Firmware Toolkit.

These configuration fragments are available to rebuild kernels or can be used as examples to configure then build
your own customized kernels.

Fragments are stored in two distinct sublfolders according to the nature of provided features. Either hardware support or functionality support in the kernel.

Features are assigned to independant axis ***functional *** and ***hardware *** axis. This let you enable or not a given feature on a given hardware.
On both axis, features are stored grouped into folders by function type. Each set of functionality is stored into a distinct file that should be included from kernel Makefile (please see documantation and howtos from in Makefiles section).
* The ***functional*** features are grouped into the following categories (or subfolers)
  * containers (which activate cgroups and namespaces, virtualization is below)
  * crypto (cryptography support)
  * debug (kernel debug and traces support)
  * filesystems (supported filesystems)
  * network (network features support)
  * security (security support)
  * virtualization (virtualization support)

* The ***hardware*** feature axis
  * board-bluerints (board and architectures specific features)
  * device-drivers (device support which can be reused by distinct boards)
