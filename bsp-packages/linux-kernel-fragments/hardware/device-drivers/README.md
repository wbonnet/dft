# Linux kernel device drivers configuration fragments

The device-drivers folder contains Linux kernel sets of defconfig options used to activate hardware drivers provided with kernel sources.

These fragments are designed to be shared accros all boards regardless of board and kernel versions.

When building a custom kernel package, you have to ensure that hardware is available on the target board according to kernel driver options you include from you makefile.

The consistency checks upon hardware availability and support are provided by Firmware Toolkit and included in provided board Makefiles.

Kernel ragments files are allocated into directories named after kernel menuconfig entry names.

The main folders are :
  * android
  * block-devices
  * char-devices
  * graphics
  * multimedia
  *network
  * sound
  * usb