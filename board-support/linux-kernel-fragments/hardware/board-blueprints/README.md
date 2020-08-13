# Linux kernel board blueprints fragments

The board-blueprints folder contains Linux kernel sets of defconfig options used to activate support of a given board.

When generating the defconfig in order to build kernel the fragment include order is
 1. The *hardware/mutual* definitions
 2. The board blueprint, updating mutual definitions
 3. The *hardware/device-drivers* definition according to list from Makefile
 4. The *functional* fragments are included according to list from Makefile

Each board definition is stored in a separate file named after the board (same as in board-catalog.yml) ex: orangepi-zero.defconfig

There must be only one board blueprint included in a kernel production manifest. Otherwise, you are assuming this decision and doing it at your own risks. No configuration consistancy can be provided by Firmware Toolkit.