# Linux kernel board blueprints fragments

The board-blueprints folder contains Linux kernel sets of defconfig options used to activate support of a given board.

When generating the defconfig in order to build kernel the fragment include order is
 # The *hardware/mutual* definitions
 # The board blueprint, updating mutual definitions
 # The *hardware/device-drivers* definition according to list from Makefile
 # Finaly *functional* fragments are included according to list from Makefile

Each board definition is stored in a file named after the board (same as in board-catalog.yml).

There must be only one board blueprint included in a kernel production manifest. Otherwise, you are assuming this decision and doing it at your own risks. No configuration consistancy can be provided by Firmware Toolkit.