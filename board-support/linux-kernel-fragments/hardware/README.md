# Linux kernel hardware configuration fragments

The hardware folder contains Linux kernel configuration fragments grouped by functional categories.
Each category is assigned to a folder storing one or several fragments (files) defining sets of features (network, security, etc.) which can be activated separatly and or in addition of your own fragments.

The ***hardware*** folder contains definition for :
  * mutual (the mutual layer is the basic set of defconfig options shared accros all boards. This set is and applied first before any other config overlay).
  * board blueprints (defining in board distinct files the minimal set of options to suppord board specific components, hardware dependant functionalities, etc.)
  * device drivers (devices definition can be shared accross distinct boards using the same hardware. Nonetheless distinct compilations are needed to match kernel symbols)