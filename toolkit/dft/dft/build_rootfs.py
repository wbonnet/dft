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

""" This modules iplements the functionnalities needed to create a rootfs installation
based upon the definition stored in a configuration file and a set of Ansible roles.
"""

import logging
import os
import tempfile
from distutils import dir_util
from distutils import file_util
from cli_command import CliCommand
from model import Key


#
#    Class BuildRootFS
#
class BuildRootFS(CliCommand):
  """This class implements method needed to create the Root FileSystem

  The Key.ROOTFS.value is the initial installation of Debian (debootstrap) which
  is used to apply ansible playbooks.

  The methods implemented in this class provides what is needed to :
  . create the debootstrap (chrooted environment)
  . handle filesystems like dev and proc in the chrooted environment
  . copy DFT and project specific templates into /dft_bootstrap
  . run ansible in the chroot
  . cleanup things when installation is done
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

    # Path to the ansible roles under dft_base
    self.ansible_dir = project.project[Key.CONFIGURATION.value][Key.DFT_BASE.value] + "/ansible"

    # Set the log level from the configuration
    print("setting logs " + project.dft.log_level)
    logging.basicConfig(level=project.dft.log_level)

  # -------------------------------------------------------------------------
  #
  # create_rootfs
  #
  # -------------------------------------------------------------------------
  def create_rootfs(self):
    """This method implement the business logic of generating the rootfs.
    It calls dedicated method for each step. The main steps are :

    . setting up working directory
    . setup QEMU and run stage 2 if needed
    . deploy DFT Ansible templates, and run Ansible to do confiugration
    . cleanup installation files
    . cleanup QEMU if needed
    """

    # Check that DFT path is valid
    if not os.path.isdir(self.ansible_dir):
      logging.critical("Path to DFT installation is not valid : %s. Ansible directory is missing",
                       self.project.project[Key.CONFIGURATION.value][Key.DFT_BASE.value])
      exit(1)

    # Ensure target rootfs mountpoint exists and is a dir
    if not os.path.isdir(self.project.get_rootfs_mountpoint()):
      os.makedirs(self.project.get_rootfs_mountpoint())
    else:
      if (Key.KEEP_ROOTFS_HISTORY.value in self.project.project[Key.CONFIGURATION.value] and
          self.project.project[Key.CONFIGURATION.value][Key.KEEP_ROOTFS_HISTORY.value]):
        logging.warning("target rootfs mount point already exists : " +
                        self.project.get_rootfs_mountpoint())
        exit(1)
      else:

# TODO security hole !!!!!
# Protect path generation to avoid to remove / !!!
        sudo_command = 'sudo rm -fr "' + self.project.get_rootfs_mountpoint() +'"'
        self.execute_command(sudo_command)
        os.makedirs(self.project.get_rootfs_mountpoint())

    # Create the bootstrap directory
    dft_target_path = self.project.get_rootfs_mountpoint() + "/dft_bootstrap/"
    if not os.path.exists(dft_target_path):
      os.makedirs(dft_target_path)

    # Do the debootstrap call
    self.generate_debootstrap_rootfs()

    # Launch Ansible to install roles identified in configuration file
    self.install_packages()

    # Launch Ansible to install roles identified in configuration file
    self.generate_fstab()

    # Setup the chrooted environment (mount bind dev and proc
    self.teardown_chrooted_environment()

    # Once installation has been played, we need to do some cleanup
    # like ensute that no mount bind is still mounted, or delete the
    # DFT ansible files
    self.cleanup_installation_files()

    # Remove QEMU if it has been isntalled. It has to be done in the end
    # since some cleanup tasks could need QEMU
    if self.use_qemu_static:
      self.cleanup_qemu()

    # Final log
    logging.info("RootFS has been successfully generated into : " +
                 self.project.get_rootfs_mountpoint())

  # -------------------------------------------------------------------------
  #
  # install_packages
  #
  # -------------------------------------------------------------------------
  def install_packages(self):
    """This method remove the QEMU static binary which has been previously
    copied to the target
    """

    logging.info("installing packages")

    # Create the target directory. DFT files will be installed under this
    # directory.
    try:
      logging.debug("copying DFT toolkit")

      # Check that target directory is in the rootfs. It has been previously created at the same
      # time as the mountpoint. This test check for both bootstrap and mountpoint.
      dft_target_path = self.project.get_rootfs_mountpoint() + "/dft_bootstrap/"
      if not os.path.exists(dft_target_path):
        logging.debug("creating dft_bootstrap under " + dft_target_path)
        os.makedirs(dft_target_path)
        logging.debug("created !")
      else:
        logging.debug("dft_bootstrap already exist under " + dft_target_path)

      # Copy the DFT toolkit content to the target rootfs
      for copy_target in os.listdir(self.ansible_dir):
        logging.debug("Copy the DFT toolkit : preparing to copy " + copy_target)
        copy_target_path = os.path.join(self.ansible_dir, copy_target)
        if os.path.isfile(copy_target_path):
          logging.debug("copying file " + copy_target_path + " => " + dft_target_path)
          file_util.copy_file(copy_target_path, dft_target_path)
        else:
          logging.debug("copying tree " + copy_target_path + " => " + dft_target_path)
          dir_util.copy_tree(copy_target_path, os.path.join(dft_target_path, copy_target))

      # Copy the additional toolkit content to the target rootfs
      if Key.ADDITIONAL_ROLES.value in self.project.project[Key.CONFIGURATION.value]:
        for additional_path in self.project.project[Key.CONFIGURATION.value]\
                                                   [Key.ADDITIONAL_ROLES.value]:
          logging.debug("Copy the additional toolkit : preparing to copy from additional path "
                        + additional_path)
          for copy_target in os.listdir(additional_path):
            logging.debug("Copy the additional toolkit : preparing to copy " + copy_target)
            copy_target_path = os.path.join(additional_path, copy_target)
            if os.path.isfile(copy_target_path):
              logging.debug("copying file " + copy_target_path + " => " + dft_target_path)
              file_util.copy_file(copy_target_path, dft_target_path)
            else:
              logging.debug("copying tree " + copy_target_path + " => " + dft_target_path)
              dir_util.copy_tree(copy_target_path, os.path.join(dft_target_path, copy_target))

    except OSError as exception:
      # Call clean up to umount /proc and /dev
      self.cleanup_installation_files()
      logging.critical("Error: %s - %s.", exception.filename, exception.strerror)
      exit(1)

    # Flag if someroles has been foundand added to site.yml
    role_has_been_found = False

    # Generate the site file including all the roles from rootfs
    # configuration, then move  roles to the target rootfs
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
      # Generate file header
      working_file.write("# Defines the role associated to the rootfs being generated\n")
      working_file.write("---\n")
      working_file.write("- hosts: local\n")
      working_file.write("\n")

      # Test if some variable files have to be included
      if Key.VARIABLES.value in self.project.project[Key.PROJECT_DEFINITION.value]:
        # Yes, then output the vars_files marker
        working_file.write("  vars_files:\n")

        # And iterate the list of files containing variables
        for vars_file in self.project.project[Key.PROJECT_DEFINITION.value]\
                                                 [Key.VARIABLES.value]:
          # Append the file to the site.yml file
          working_file.write("  - " + vars_file + "\n")
          logging.debug("Adding variables file " + vars_file)

          # Complete the path to have a full path on disk (in case of path local
          # to where is located the project file)
          vars_file = self.project.generate_def_file_path(vars_file)

          # Copy the variabes fies to the bootstrap directory
          logging.debug("Copy the variables file : preparing to copy " + vars_file)
          if os.path.isfile(vars_file):
            logging.debug("copying file " + vars_file + " => " + dft_target_path)
            file_util.copy_file(vars_file, dft_target_path)
          else:
            logging.error("Variable files " + vars_file + " is not a file")
            logging.error("Skipping this file")

        # Just some spacing for pretty printing
        working_file.write("\n")

      working_file.write("  roles:\n")

      # Iterate the list of distributions loaded from the file
      for role in self.project.rootfs[Key.ROLES.value]:
        # At least one role has beenfound, flag it
        role_has_been_found = True
        logging.debug("Adding role " + role)
        working_file.write("  - " + role + "\n")

    # We are done with file generation, close it now
    working_file.close()

    # Generate the file path
    filepath = self.project.get_rootfs_mountpoint() + "/dft_bootstrap/site.yml"

    # Finally move the temporary file under the rootfs tree
    sudo_command = "sudo mv -f " + working_file.name + " " + filepath
    self.execute_command(sudo_command)

    # Warn the user if no role is found. In such case rootfs will be same
    # debotstrap, which is certainly not what is expected
    if not role_has_been_found:
      logging.warning("No role has been found in rootfs definition. Rootfs is same as debootstrap \
                       output")
      logging.error("You may wish to have a look to : " + self.project.generate_def_file_path(\
                      self.project.project[Key.PROJECT_DEFINITION.value][Key.ROOTFS.value][0]))

    # Generate the command line to execute Ansible in the chrooted environment
    logging.info("running ansible")
    sudo_command = "LANG=C sudo chroot " + self.project.get_rootfs_mountpoint()
    sudo_command += " /bin/bash -c \"cd /dft_bootstrap && /usr/bin/ansible-playbook -i "
    sudo_command += " inventory.yml -c local site.yml\""
    self.execute_command(sudo_command)
    logging.info("ansible stage successfull")


  # -------------------------------------------------------------------------
  #
  # generate_build_number
  #
  # -------------------------------------------------------------------------
  def generate_build_number(self):
    """ Generate a version number in /etc/dft_version file. This is used
    to keep track of generation date.
    """

    logging.info("generating build number")

    # Open the file and writes the timestamp in it
    filepath = self.project.get_rootfs_mountpoint() + "/etc/dft_version"
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
      working_file.write("DFT-" + self.project.timestamp + "\n")
    working_file.close()

    sudo_command = "sudo mv -f " + working_file.name + " " + filepath
    self.execute_command(sudo_command)



  # -------------------------------------------------------------------------
  #
  # generate_debootstrap_rootfs
  #
  # -------------------------------------------------------------------------
  def generate_debootstrap_rootfs(self):
    """ This method run deboostrap to create the initial rootfs.
    """

    logging.info("generating debootstrap rootfs")

    # Generate the base debootstrap command
    debootstrap_command = "sudo debootstrap --no-check-gpg"

    # Add the foreign and arch only if they are different from host, and
    # thus if use_qemu_static is True
    if self.use_qemu_static:
      logging.info("running debootstrap stage 1")
      debootstrap_command += " --foreign --arch=" + self.project.get_target_arch()
    else:
      logging.info("running debootstrap")

    # Add the target, mount point and repository url to the debootstrap command
    debootstrap_command += " " +  self.project.get_target_version() + " "
    debootstrap_command += self.project.get_rootfs_mountpoint() + " "
    debootstrap_command += self.project.project[Key.PROJECT_DEFINITION.value]\
                                                   [Key.DEBOOTSTRAP_REPOSITORY.value]

    # Finally run the subprocess
    self.execute_command(debootstrap_command)

    # Check if we are working with foreign arch
    if self.use_qemu_static:
      # QEMU is used, and we have to install it into the target
      self.setup_qemu()

      # And second stage must be run
      logging.info("doing debootstrap stage 2")
      debootstrap_command = "LANG=C sudo chroot " + self.project.get_rootfs_mountpoint()
      debootstrap_command += " /debootstrap/debootstrap --second-stage"
      self.execute_command(debootstrap_command)

    # Setup the chrooted environment (mount bind dev and proc
    self.setup_chrooted_environment()

    # Update the APT sources
    self.generate_apt_sources()

    # Then update the list of packages
    self.update_package_catalog()

    # Install extra packages into the chroot
    self.install_package("apt-utils ansible")

    # Generate a unique build timestamp into /etc/dft_version
    self.generate_build_number()



  # -------------------------------------------------------------------------
  #
  # generate_apt_sources
  #
  # -------------------------------------------------------------------------
  def generate_apt_sources(self):
    """ This method has two functions, configure APT sources and configure
    apt to ignore validity check on expired repositories

    The method generates a file named 10no-check-valid-until which is
    placed in the apt config directory. It is used to deactivate validity
    check on repository during installation, so a mirror can still be used
    even if it is expired. This use case happens often when mirrors cannot
    be sync'ed automatically from the internet

    Second part of the methods iterate the repositories from configuration
    file and generates sources.list
    """
    logging.info("generating APT sources configuration")

    # Test if the generate_validity_check is defined, if not set the default value
    if Key.GENERATE_VALIDITY_CHECK.value not in self.project.project[Key.CONFIGURATION.value]:
      self.project.project[Key.CONFIGURATION.value][Key.GENERATE_VALIDITY_CHECK.value] = True

    # Test if we have to generate the no-check-valid_until file
    if self.project.project[Key.CONFIGURATION.value][Key.GENERATE_VALIDITY_CHECK.value]:
      logging.debug("generating /etc/apt/apt.conf.d/10no-check-valid-until")

      # Generate the file path
      filepath = self.project.get_rootfs_mountpoint() + "/etc/apt/apt.conf.d/10no-check-valid-until"

      # Open the file and writes configuration in it
      with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
        working_file.write("Acquire::Check-Valid-Until \"0\";\n")
      working_file.close()

      sudo_command = "sudo mv -f " + working_file.name + " " + filepath
      self.execute_command(sudo_command)
    # If generation is deactivated, only output a debug message
    else:
      logging.debug("/etc/apt/apt.conf.d/10no-check-valid-until generation is deactivated")

    # Generate the file path
    filepath = self.project.get_rootfs_mountpoint() + "/etc/apt/sources.list"

    # Open the file and writes configuration in it
    self.project.debian_mirror_url = self.project.project[Key.PROJECT_DEFINITION.value]\
                                                             [Key.DEBOOTSTRAP_REPOSITORY.value]

    # Flag if we have found a matching distro or not
    distro_has_been_found = False

    # The open the temp file for output, and iterate the distro dictionnary
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
      # Iterate the list of distributions loaded from the file
      for distro in self.project.repositories[Key.DISTRIBUTIONS.value]:
        logging.debug(distro)
        # Process only if it is the version we target
        if distro[Key.NAME.value] == self.project.get_target_version() and \
                                     self.project.get_target_arch() in \
                                     distro[Key.ARCHITECTURES.value]:
          # W have found a matching distro or not
          distro_has_been_found = True
          # Then iterate all the sources for this distro version
          for repo in distro[Key.REPOSITORIES.value]:
            logging.debug(repo)

            # Test if deb line has to be generated
            if (Key.GENERATE_DEB.value not in repo) or (Key.GENERATE_DEB.value in repo and \
                                                        repo[Key.GENERATE_DEB.value]):
              # Will generate the deb line only if the key
              # generate-deb is present and set to True or the key
              # is not present
              working_file.write("deb " + repo[Key.URL.value] +" " + repo[Key.SUITE.value] + " ")
              for section in repo[Key.SECTIONS.value]:
                working_file.write(section + " ")
              working_file.write("\n")

            # Test if deb-src line has also to be generated
            if Key.GENERATE_SRC.value in repo:
              # Will generate the deb-src line only if the key
              # generate-src is present and set to True
              if repo[Key.GENERATE_SRC.value]:
                working_file.write("deb-src " + repo[Key.URL.value] + " " +
                                   repo[Key.SUITE.value] + " ")
                for section in repo[Key.SECTIONS.value]:
                  working_file.write(section + " ")
                working_file.write("\n")

    # Warn the user if no matching distro is found. There will be an empty
    # /etc/apt/sources.list and installation will faill
    if not distro_has_been_found:
      self.cleanup_installation_files()
      logging.error("No distribution matching " + self.project.get_target_version())
      logging.error("Please check repositories definition for this project.")
      logging.error("File in use is : " + self.project.generate_def_file_path(\
                                self.project.project[Key.PROJECT_DEFINITION.value]\
                                                        [Key.REPOSITORIES.value][0]))
      logging.critical("Cannot generate /etc/apt/sources.list under rootfs path. Operation is \
                        aborted !")
      exit(1)

    # Its done, now close the temporary file
    working_file.close()

    # Finally move the temporary file under the rootfs tree
    sudo_command = "sudo mv -f " + working_file.name + " " + filepath
    self.execute_command(sudo_command)

  # -------------------------------------------------------------------------
  #
  # generate_fstab
  #
  # -------------------------------------------------------------------------
  def generate_fstab(self):
    """ This method is in charge of generating the file systems table
    configuration file. Aka /etc/fstab.

    This table describes the various file systems to mount into the rootfs
    during the boot process. The file systems can override the definition
    fromvthe initial boot, before changing root to firware.

    If the rootfs is used in standard mode (not a squashfs based firmware),
    then this file is the only fstab know and used by the system.

    File systems definition if done in the image.yml file. Information are
    shared between build_rootfs and build_mage targets.
    """
    logging.info("generating fstab configuration file")

    # Check if the filesystems key is defined in image
    if Key.FILESYSTEMS.value not in self.project.image:
      logging.debug("No filesystems definition in image file. Nothing to do for fstab generation")
      return

    # Generated the base path to the file to create
    filepath = self.project.get_rootfs_mountpoint() + "/etc/fstab"

    # Generate a temporary file that will be filed then moved under /etc/fstab
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
      for fileSystem in self.project.image[Key.FILESYSTEMS.value]:
        print(fileSystem)
        # Generate one by one the different fields of the filesystem lines
        working_file.write(fileSystem[Key.FILESYSTEM.value])
        working_file.write(" ")
        working_file.write(fileSystem[Key.MOUNTPOINT.value])
        working_file.write(" ")
        working_file.write(fileSystem[Key.TYPE.value])
        working_file.write(" ")
        working_file.write(fileSystem[Key.OPTIONS.value])
        working_file.write(" ")
        working_file.write(fileSystem[Key.DUMP.value])
        working_file.write(" ")
        working_file.write(fileSystem[Key.PASS.value])
        working_file.write("\n")

    # Move the temporary file under the rootfs tree
    sudo_command = "sudo mv -f " + working_file.name + " " + filepath
    print(sudo_command)
    self.execute_command(sudo_command)
