# Board support Builtin tests
The *sbit* folder contains the unit tests used to validate board support by rootfs board specific images. 

These test suites are defined by unit test description files and target the validation of kernel and BSP installation for a given board.

Checks are done to verify kernel features activation, drivers availability, hardware and network support, etc.

These tests are operating level system level tests and hardware dependent tests. Thus there exist one test suite per distinct board. 

Software level tests are available from the sbit folder in board-images. Software level tests are hardware independent tests. There exist one test suite per on image flavor.

Testing a board requires to successfuly execute both hardware and software tests. 

Even if software tests are succesfull they should not been considered as successful as long as hardware haven't been also executed successfully as a prerequiste.

