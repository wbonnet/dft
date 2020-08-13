# Board images
This folder contains the resources  used to produce the bootable whose defintions are provided with ***FirmwareToolkit***

Such as BSP production, image production is Makefile driven. The ***make*** command is in charge of orchestration of calls made to  build tools.
This allow users to execute the build steps by hand, replay process and customize execution.

The build process configuration is controled by a file named blueprint-***boardname***.yml. This file is a YAML configuration file for the ***DFT*** tool used to specify which BSP should be installed for this board and how.

The directory tree is organized with ***category*** level folder contaning a distinct folder for each board assigne to this category.

* The following categories are availables :
  * desktop
  * devkit (*Development Kit*)
  * laptop
  * phone
  * set-top-box (*STB*)
  * single-board-computer (*SBC*)
  * tablet

The board support package definitions are stored in a separate folder, board-support, at the same level as this folder. Please keep in mind that images use packages produced by board-support resources in their definition.
