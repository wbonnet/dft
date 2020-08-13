# Board support resources
The folder board-support contains resources (build descriptions, configuration files, Makefiles, ...) needed to produce the binaries used to support boards (kernel, u-boot, etc.)

Board definitions are allocated into category folders (single-board-computer, laptop, etc.).

The board support resources include materials needed for production of both ***BSP*** itself and generation of the bootable images using this BSP for supported boards.

Binaries production is Makefile driven. Make command is in charge of making calls to the dedicated build tools and synchronize tools execution.
This allow users to execute the build steps by hand, replay process and customize execution.

The build and packaging process is controled with two configuration files :
* bsp-boardname.mk a Makefile include defining how to build the ***BSP*** packages (in Makefile syntax)
* blueprint-boardname.yml a YAML configuration file for the ***DFT*** tool used to specify which BSP should be installed for this board and how.

The bord images are in a separate folder at the same level as board-support. Images use these resources in their build definition.