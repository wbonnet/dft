# Linux kernel board blueprints configuration fragments









The mutual folder contains Linux kernel sets of defconfig options shared accros all boards regardless of board hardware nor kernel versions.

The *mutual* configurations should be seen as the common defconfig ancestor, used by Firmware Toolkit for Linux kernel production, when generating configuration files.

Thus *mutual* should be included first, before *hardware* or *functional* fragments in the kernel Makefiles.
