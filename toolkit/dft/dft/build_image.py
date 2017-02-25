#
# The contents of this file are subject to the Apache 2.0 license you may not
# use this file except in compliance with the License.
#
# Software distributed under the License is distributed on an "AS IS" basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
#
# Copyright 2016 DFT project (http://www.debianfirmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
# Debian Firmware Toolkit is the new name of Linux Firmware From Scratch
# Copyright 2014 LFFS project (http://www.linuxfirmwarefromscratch.org).
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

import logging
import os
import subprocess
import tarfile
import shutil
import tempfile
import distutils
from distutils import file_util
from distutils import dir_util
from cli_command import CliCommand

#
#    Class BuildImage
#
class BuildImage(CliCommand): 
  """This class implements method needed to build the image which will be
  written in flash memory or on a SD card.
  """

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self, dft, project):
    """Default constructor
    """

    # Initialize ancestor
    CliCommand.__init__(self, dft, project)

  # -------------------------------------------------------------------------
  #
  # build_image
  #
  # -------------------------------------------------------------------------
  def build_image(self):
    """This method implement the business logic of image generation. Image
    is a file containing the dump of what will be copied on the target 
    storage device (harddisk or flash for example). It calls dedicated 
    method for each step. The main steps are :

    .
    """

    logging.critical("Not yet available")
    exit(1)
