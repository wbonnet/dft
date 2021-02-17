# u-boot assembly scripts
This folder contains the scripts needed to finalize the production of u-boot binary for boards using a trusted bootchain  such as ARM64 boards.

These scripts are in charge of assembling the different binary parts of the u-boot from compilation stage and signing the final binary.

Scripts content are depend on board vendor procedures, and may download binaries from vendor web site ine case of BLOBs published without plublicly available sources (especially for signature step).

Assembly scripts are run by the Makefile framework during execution of the package target. Depending on vendors procedures there can exist distinct different scrpts perd board, par SOC, per vendor or any combination according to vendors desoign.

The produced binaries produced by the execution of the scripts are shipped within by the debian package and referenced by the installation procedure also shipped within the given package.
