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
# Copyright 2016 DFT project (http://www.firmwaretoolkit.org).
# All rights reserved. Use is subject to license terms.
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

""" This modules iplements the functionnalities needed to create a rootfs installation
based upon the definition stored in a configuration file and a set of Ansible roles.
"""

import logging
import os
import glob
import tempfile
import errno
from shutil import rmtree
from distutils import dir_util
from distutils import file_util
from dft.cli_command import CliCommand
from dft.enumkey import Key


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
    self.ansible_roles_dir = project.get_dft_base()  + "/ansible-roles"

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
    if not os.path.isdir(self.ansible_roles_dir):
      logging.critical("Path to DFT installation is not valid : %s. Ansible directory is missing",
                       self.project.get_dft_base())
      logging.critical("self.project.get_dft_base : %s", self.project.get_dft_base())
      logging.critical("self.ansible_roles_dir : %s", self.ansible_roles_dir)
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
        rmtree(self.project.get_rootfs_mountpoint())
        os.makedirs(self.project.get_rootfs_mountpoint())

    # Create the bootstrap directory
    dft_target_path = self.project.get_rootfs_mountpoint() + "/dft_bootstrap/"
    os.makedirs(dft_target_path, exist_ok=True)

    # Do the debootstrap call
    self.generate_debootstrap_rootfs()

    # Launch Ansible to install roles identified in configuration file
    self.install_packages()

    # Finally run a full upgrade in case of source modification during install
    # Allow downgrades is needed if pinning has been modified by Ansible roles
    self.upgrade_packages(allow_downgrades=True)

    # Launch Ansible to install roles identified in configuration file
    self.generate_fstab()

    # Setup the chrooted environment (mount bind dev and proc
    self.teardown_chrooted_environment()

    # Instqllqtion is finished, remove all downloaded .deb files if flag
    # is activated. This will save a few tens to a few hundreds MB
    self.remove_downloaded_archives()

    # Once installation has been played, we need to do some cleanup
    # like ensute that no mount bind is still mounted, or delete the
    # DFT ansible files
    self.cleanup()

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
        os.makedirs(dft_target_path, exist_ok=True)
        logging.debug("created !")
      else:
        logging.debug("dft_bootstrap already exist under " + dft_target_path)

      # Copy the DFT toolkit content to the target rootfs
      for copy_target in os.listdir(self.ansible_roles_dir):
        logging.debug("Copy the DFT toolkit : preparing to copy " + copy_target)
        copy_target_path = os.path.join(self.ansible_roles_dir, copy_target)
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
      self.cleanup()
      logging.critical("Error: %s - %s.", exception.filename, exception.strerror)
      exit(1)

    # Flag if some roles have been found and added to site.yml
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
          logging.info("Adding variables file " + vars_file)

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
        logging.info("Adding role " + role)
        working_file.write("  - " + role + "\n")

    # We are done with file generation, close it now
    working_file.close()

    # Generate the file path
    filepath = self.project.get_rootfs_mountpoint() + "/dft_bootstrap/site.yml"

    # Finally move the temporary file under the rootfs tree
    command = "mv -f " + working_file.name + " " + filepath
    self.execute_command(command)

    # Warn the user if no role is found. In such case rootfs will be same
    # debotstrap, which is certainly not what is expected
    if not role_has_been_found:
      logging.warning("No role has been found in the rootfs content definition. The generated \
                       rootfs contains only debootstrap default output")
      logging.error("You may wish to have a look to : " + self.project.generate_def_file_path(\
                      self.project.project[Key.PROJECT_DEFINITION.value][Key.ROOTFS.value][0]))

    # Generate the command line to execute Ansible in the chrooted environment
    # The HOME variable is redefined to prevent creation of an extra dir in home of the chroot
    logging.info("now running ansible-playbook to deploy packages and roles inside the chrooted environment")
    command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
    command += " /bin/bash -c \"cd /dft_bootstrap && HOME=/root /usr/bin/ansible-playbook -i"
    command += " inventory.yml -c local site.yml -e ansible_python_interpreter=/usr/bin/python3\""
    self.execute_command(command)

    # Depending on Ansible version, a .rnd file and two directories may be left in /root
    # The following commands do the cleanup
    command = "rm -f " + self.project.get_rootfs_mountpoint() + "/root/.rnd"
    self.execute_command(command)

    command = "rmdir " + self.project.get_rootfs_mountpoint() + "/root/.ansible/tmp/"
    self.execute_command(command)

    command = "rmdir " + self.project.get_rootfs_mountpoint() + "/root/.ansible/"
    self.execute_command(command)


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

    command = "mv -f " + working_file.name + " " + filepath
    self.execute_command(command)



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
    debootstrap_command = "debootstrap --no-check-gpg"

    # Check if the target is different from host dpkg arch. If yes, a --arch flag
    # Needs to be appended to debootstrap call. It does not mean that qemu muse be
    # used (64 kernels can run 32 bits userland). QEMU use is checked next
    if self.use_debootstrap_arch:
      debootstrap_command += " --arch=" + self.project.get_target_arch()

      # Add the foreign flag if host and target are different (ie: amd64 and armhf)
      if self.use_qemu_static:
        logging.info("running debootstrap stage 1")
        debootstrap_command += " --foreign"
    else:
      logging.info("running debootstrap")

    # Include gnupg package in the list of software installed in the deboostrap chroot
    debootstrap_command += " --include=gnupg,dirmngr,apt-transport-https"

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
      debootstrap_command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
      debootstrap_command += " /debootstrap/debootstrap --second-stage"
      self.execute_command(debootstrap_command)

    # Setup the chrooted environment (mount bind dev and proc
    self.setup_chrooted_environment()

    # Update the APT sources
    self.generate_apt_sources()

    # Update the APT preferences
    self.generate_apt_preferences()

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

      command = "mv -f " + working_file.name + " " + filepath
      self.execute_command(command)
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
        logging.debug("distro : ")
        logging.debug(distro)

        # Process only if it is the version we target
        if distro[Key.NAME.value] != self.project.get_target_version() or \
                                     self.project.get_target_arch() not in \
                                     distro[Key.ARCHITECTURES.value]:
          # No matching move to next item
          continue

        # It is a match, we have found a matching distro or not
        distro_has_been_found = True
        # Then iterate all the sources for this distro version
        for repo in distro[Key.REPOSITORIES.value]:
          logging.debug("repo : ")
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

          # Check if there is a pubkey to retrieve using gpg key server
          if Key.PUBKEY_GPG.value in repo:
            key_gpg = repo[Key.PUBKEY_GPG.value]
            logging.debug("retrieving public key : " + key_gpg)

            # Add a key to the know catalog signing keys
            self.add_catalog_signing_key(key_gpg)

          # Check if there is a pubkey to retrieve using its url
          if Key.PUBKEY_URL.value in repo:
            key_url = repo[Key.PUBKEY_URL.value]
            logging.debug("retrieving public key : " + key_url)

            # Generate the retrieve and add command
            command = "chroot " + self.project.get_rootfs_mountpoint() + " bash -c "
            command += "'/usr/bin/wget -qO - " + repo[Key.PUBKEY_URL.value]
            command += " | /usr/bin/apt-key add -'"
            self.execute_command(command)

    # Warn the user if no matching distro is found. There will be an empty
    # /etc/apt/sources.list and installation will faill
    if not distro_has_been_found:
      self.cleanup()
      logging.error("No distribution matching " + self.project.get_target_version() + " / " +
                    self.project.get_target_arch())
      logging.error("Please check repositories definition for this project.")
      logging.error("Repositories file is : " + self.project.generate_def_file_path(\
                                    self.project.project[Key.PROJECT_DEFINITION.value]\
                                                        [Key.REPOSITORIES.value][0]))
      logging.critical("Cannot generate /etc/apt/sources.list under rootfs path. Operation is \
                        aborted !")
      exit(1)

    # Its done, now close the temporary file
    working_file.close()

    # Finally move the temporary file under the rootfs tree
    command = "mv -f " + working_file.name + " " + filepath
    self.execute_command(command)



  # -------------------------------------------------------------------------
  #
  # generate_apt_preferences
  #
  # -------------------------------------------------------------------------
  def generate_apt_preferences(self):
    """ This method generates the configuration files stored under
    /etc/apt/preferences.d

    Current implementation handles only pinning file. This file is generated
    from the information contained in the repositories.yml file, defined
    under the pinning: entry.

    The pinning antry contains a list of pin items. Each list entry is a set
    of three lines in the pinning file.

    Please see https://wiki.debian.org/AptPreferences for more information
    about defining preferences
    """
    logging.info("generating APT configuration")

    # Test if the generate_validity_check is defined, if not set the default value
    if Key.PINNING.value not in self.project.repositories:
      logging.debug("Pinning is not defined in the repository file. Nothing to do.")
      return

    # The pinning entry is defined, let's iterate it and generate pinning file
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
      # Iterate the list of distributions loaded from the file
      for pin_entry in self.project.repositories[Key.PINNING.value]:
        # Check that the three entries are defined otherwise output an error and skip
        missing_entry = False
        # Package entry must be defined
        if Key.PACKAGE.value not in pin_entry:
          logging.error("Package entry is missing, skipping : " + pin_entry)
          missing_entry = True

        # Pin entry must be defined
        if Key.PIN.value not in pin_entry:
          logging.error("Pin entry is missing, skipping : " + pin_entry)
          missing_entry = True

        # Pin-Priority entry must be defined
        if Key.PIN_PRIORITY.value not in pin_entry:
          logging.error("Pin-Priority entry is missing, skipping : " + pin_entry)
          missing_entry = True

        # Are we missing some information ?
        if missing_entry:
          # Yes, output was already sent, just skip
          continue

        # Entry is complete, let's output it to the working file
        working_file.write("Package: " + str(pin_entry[Key.PACKAGE.value]) + "\n")
        working_file.write("Pin: " + str(pin_entry[Key.PIN.value]) + "\n")
        working_file.write("Pin-Priority: " + str(pin_entry[Key.PIN_PRIORITY.value]) + "\n")
        working_file.write("\n")

    # Its done, now close the temporary file
    working_file.close()

    # Finally move the temporary file under the rootfs tree
    filepath = self.project.get_rootfs_mountpoint() + "/etc/apt/preferences.d/pinning"
    command = "mv -f " + working_file.name + " " + filepath
    self.execute_command(command)



  # -------------------------------------------------------------------------
  #
  # remove_downloaded_archives
  #
  # -------------------------------------------------------------------------
  def remove_downloaded_archives(self):
    """ This method is in charge of removing .deb files downoaded during
    installation process. The files are stored under var/cache/apt/archives

    According to the rootfs content files size vary from a few tens of MB to
    several hundreds. TReoving this files can save a lot of space from thei
    generated rootfs.

    Removal is control by the remove_downloaded_archives from the project
    configuration. Default value is True (archives are removed)
    """

    # Check if the removal flag is deactivated
    if Key.REMOVE_DOWNLOADED_ARCHIVES.value in self.project.project[Key.CONFIGURATION.value] and \
        not self.project.project[Key.CONFIGURATION.value][Key.REMOVE_DOWNLOADED_ARCHIVES.value]:
      # Yes, thus no need to remove any files just exit
      return

    # Still here ? thus remove all archives from var/cache/apt/archives
    # in the target filesystem
    filepath = self.project.get_rootfs_mountpoint()
    filepath += "/var/cache/apt/archives/*.deb"

    # Iterate the list of deb files and remove them one by one. Generating
    # a rm comand with a wildcard will not work since it is likely that it
    # expansion won't happen
    for deb_target in glob.glob(filepath):
      logging.debug("Removing " + deb_target)
      os.remove(deb_target)



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
    from the initial boot, before changing root to firware.

    If the rootfs is used in standard mode (not a squashfs based firmware),
    then this file is the only fstab know and used by the system.

    File systems definition if done in the image.yml file. Information are
    shared between build_rootfs and build_mage targets.
    """
    logging.info("generating fstab configuration file")

    # Check if the image configuration file exists
    if self.project.image is not None:
      # Yes, then, check if the filesystems key is defined in image
      if Key.FILESYSTEMS.value not in self.project.image:
        logging.debug("No filesystems definition in image file. Nothing to do for fstab generation")
        return
    else:
      logging.debug("No image in project configuration. Nothing to do for fstab generation")
      return

    # Generated the base path to the file to create
    filepath = self.project.get_rootfs_mountpoint() + "/etc/fstab"

    # Generate a temporary file that will be filed then moved under /etc/fstab
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
      for file_system in self.project.image[Key.FILESYSTEMS.value]:
        # Generate one by one the different fields of the filesystem lines
        working_file.write(file_system[Key.FILESYSTEM.value])
        working_file.write(" ")
        working_file.write(file_system[Key.MOUNTPOINT.value])
        working_file.write(" ")
        working_file.write(file_system[Key.TYPE.value])
        working_file.write(" ")
        working_file.write(file_system[Key.OPTIONS.value])
        working_file.write(" ")
        working_file.write(file_system[Key.DUMP.value])
        working_file.write(" ")
        working_file.write(file_system[Key.PASS.value])
        working_file.write("\n")

    # Move the temporary file under the rootfs tree
    command = "mv -f " + working_file.name + " " + filepath
    self.execute_command(command)


  # -------------------------------------------------------------------------
  #
  # cleanup
  #
  # -------------------------------------------------------------------------
  def cleanup(self):
    """This method is in charge of cleaning processes after Ansible has
    been launched. In some case some daemons are still running inside the
    chroot, and they have to be stopped manually, or even killed in order
    to be able to umount /dev/ and /proc from inside the chroot
    """
    self.project.logging.info("starting to cleanup installation files")

    # Delete the DFT files from the rootfs
    if not self.project.dft.keep_bootstrap_files:
      if os.path.isdir(self.project.get_rootfs_mountpoint() + "/dft_bootstrap"):
        rmtree(self.project.get_rootfs_mountpoint() + "/dft_bootstrap")
    else:
      self.project.logging.debug("keep_bootstrap_files is activated, keeping DFT bootstrap " +
                                 "files in " + self.project.get_rootfs_mountpoint() +
                                 "/dft_bootstrap")

    # Test if the generate_validity_check is defined, if not set the default value
    if "remove_validity_check" not in self.project.project["configuration"]:
      self.project.project["configuration"]["remove_validity_check"] = False

    if self.project.project["configuration"]["remove_validity_check"]:
      self.project.logging.debug("remove generated /etc/apt/apt.conf.d/10no-check-valid-until")

      # Generate the file path
      filepath = self.project.get_rootfs_mountpoint() + "/etc/apt/apt.conf.d/10no-check-valid-until"

      # Test if the file exists
      if os.path.isfile(filepath):
        try:
          os.remove(filepath)

        # Catch OSError in case of file removal error
        except OSError as err:
          # If file does not exit errno value will be ENOENT
          if err.errno != errno.ENOENT:
            # Thus if exception was caused by something else, throw it upward
            raise

    else:
      msg = "remove_validity_check is set to False. Generated "
      msg += "/etc/apt/apt.conf.d/10no-check-valid-until is not removed"
      self.project.logging.debug(msg)

    # Finally umount all the chrooted environment
    self.teardown_chrooted_environment()
