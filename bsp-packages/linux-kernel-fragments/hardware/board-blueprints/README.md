# Linux kernel board blueprints configuration fragments

The board-bluprints folder contains Linux kernel sets of defconfig options used to activate support of a given board.

The board blueprint is included in second place when generating kernel defconfig. First is always *hardware/mutual*, third is *hardware/device-drivers* and finaly *functional* fragments.

Each board definition is stored in a file named after the board (same as in board-catalog.yml). There must be only one board blueprint included in a kernel production manifest. Otherwise, you are assuming this decision and doing it at your own risks. No configuration consistancy can be provided by Firmware Toolkit.