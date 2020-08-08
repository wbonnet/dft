# Linux Kernel configuration fragments
The folder linux-kernel-fragments contains the Linux kernel configuration fragments provided with Firmware Toolkit.

These defconfig fragments are available in order to simplify kernel rebuild and can be used starting point or example to configure then build your own customized kernel.

Fragments are stored in two distinct subfolders according to the nature of the provided features which can fall under hardware support or kernel functionality support.

Features are assigned to independant axis ***functional*** and ***hardware*** axis (stored in subfolders). Thus, you can select which features are enabled or not on a given hardware. This can be used for instance to activate hardware acceleration on a given platform according to its specifications and available hardware components or accelerators.

On both axis, features are grouped into folders by function type. Each set of functionality is defined into a distinct file that should be included, at compilation time, from kernel Makefile (please see documantation and howto from in the Makefile section).

* The ***functional*** axis group features into categories (by using subfolders). Each file within a category controls the activation (or deactivation) of a set of features (security, network, etc.).
* The ***hardware*** axis provides definition for :
  * board blueprints (board and architecture specific components, hardware dependant and tight functionalities)
  * device drivers (device support which can be reused and shared accross distinct boards using the same hardware)
