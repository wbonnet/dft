# u-boot assembly scripts
This folder contains the scripts needed to finalize the production of u-boot binary for boards using a trusted bootchain  such as ARM64 boards.

These scripts are in charge of assembling the binary parts u-boot produced during compilation stages and signing the u-boot binary.

Scripts depends on board vendor procedures, and may download binaries from vendor web sites in case of BLOBs published without available sources (especially for signature step).

Assembly scripts are run by the Makefile framework during execution of the package target. Depending on vendor procedures there can exist several distinct scripts per board, SOC, vendor or any combination according to vendor design.

The binaries produced by the execution of the scripts are shipped within by the debian package and referenced by the installation procedure which is also shipped within the given package.
