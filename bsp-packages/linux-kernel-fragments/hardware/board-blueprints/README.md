# Linux kernel board blueprints fragments

The board-blueprints folder contains Linux kernel sets of defconfig options used to activate support of a given board.

When generating the defconfig in order to build kernel the fragment include order is
 * *hardware/mutual*
 * The board blueprint is included in second, updating mutual definitions.
 * *hardware/device-drivers* is included in third
 * finaly *functional* fragments ar included

Each board definition is stored in a file named after the board (same as in board-catalog.yml).

There must be only one board blueprint included in a kernel production manifest. Otherwise, you are assuming this decision and doing it at your own risks. No configuration consistancy can be provided by Firmware Toolkit.