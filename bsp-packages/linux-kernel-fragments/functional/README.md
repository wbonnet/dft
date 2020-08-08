# Linux Kernel functional categories

The functional folder contains Linux kernel configuration fragments grouped by functional categories.
Each category is assigned to a folder storing one or several fragments (files) defining sets of features (network, security, etc.) which can be activated separatly and or in addition of your own fragments.

* The ***functional*** features are grouped into the following categories (or subfolders). Each file within a category sontrol the activation (or deactivation) of a sets of features):
  * containers (activate cgroups and namespaces, virtualization is below)
  * crypto (cryptography functionalities)
  * debug (kernel debug and trace functionalities)
  * filesystems (filesystems support)
  * network (network functionalities)
  * security (security functionalities)
  * virtualization (virtualization functionalities)

