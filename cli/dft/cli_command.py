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
# Debian Firmware Toolkit is the new name of Linux Firmware From Scratch
# Copyright 2014 LFFS project (http://www.linuxfirmwarefromscratch.org).
#
#
# Contributors list :
#
#    William Bonnet     wllmbnnt@gmail.com, wbonnet@theitmakers.com
#
#

""" This module implements The base class and functionnalities used by all the
cli targets.
"""

import os
import stat
import subprocess
import logging
import tempfile
import errno
from enum import Enum
from dft.enumkey import Key
from dft.ansi_colors import Colors


#-----------------------------------------------------------------------------
#
# class Output
#
# -----------------------------------------------------------------------------
class Output(Enum):
  """This class defines the destination when outputing strings. It can be
  either a log level or stdout.
  """

  # Define each and every key and associated string used in the tool
  DEBUG = "debug"
  INFO = "info"
  WARNING = "warning"
  ERROR = "error"
  CRITICAL = "critical"
  STDOUT = "stdout"



#-----------------------------------------------------------------------------
#
# class Code
#
# -----------------------------------------------------------------------------
class Code(Enum):
  """This class defines the different vales for result code when outputing a
  string ended by a result code.
  """

  # Define each and every key and associated string used in the tool
  SUCCESS = " OK "
  FAILURE = " KO "
  WARNING = "Warn"



# -----------------------------------------------------------------------------
#
#    Class CliCommand
#
# -----------------------------------------------------------------------------
class CliCommand(object):
  """This class implements the base class used for all command fro cli

     It provides method used in all the derivated command, such has
     command execution and error handling, qemu setup and tear down, etc
  """

  # pylint: disable=too-many-instance-attributes

  # -------------------------------------------------------------------------
  #
  # __init__
  #
  # -------------------------------------------------------------------------
  def __init__(self, dft, project):
    """Default constructor
    """

    # Object storing the tool configuration. This object holds all the
    # definition of global configuration variales, such as tool installation
    # path, archive use, log level, etc
    self.dft = dft

    # Object storing the project definition. Project holds all the
    # configuration and definition used by the different stage of
    # the toolchain, including rootfs definition
    self.project = project

    # Retrieve the architecture of the host
    self.host_arch = subprocess.check_output("uname -m", shell=True).decode(Key.UTF8.value).rstrip()

    # Subsititude arch synonyms to have coherence between tools output
    if self.host_arch == "x86_64":
      self.host_arch = "amd64"

    if self.host_arch == "armv7l":
      self.host_arch = "armhf"

    if self.host_arch == "aarch64":
      self.host_arch = "arm64"

    # Retrieve the architecture used by dpkg. This may be different in case of 32 bits systems
    # running with a 64 bits kernel. Example : kernel is ppc64, host userland is powerpc
    self.dpkg_arch = subprocess.check_output("dpkg --print-architecture",
                                             shell=True).decode(Key.UTF8.value).rstrip()

    # Boolean used to flag the use of QEMU static
    self.use_qemu_static = (self.host_arch != project.get_target_arch())
    self.use_debootstrap_arch = (self.dpkg_arch != project.get_target_arch())
    self.qemu_binary = None

    self.project.logging.debug("host_arch " + self.host_arch)
    self.project.logging.debug("target_arch " + project.get_target_arch())
    self.project.logging.debug("dpkg_arch " + self.dpkg_arch)

    # Flags used to remove 'mount bind' states
    self.proc_is_mounted = False
    self.devpts_is_mounted = False
    self.devshm_is_mounted = False

    # Flag used to prevent multiple call to cleanup since cleanup is used
    # in exception processing
    self.cleanup_in_progress = False

    # Defines the nuùber of column used to align text when outputing with right align
    # and the real size in char (without ansi escape codes) or the code
    self.right_align = 80
    self.len_str_code = 6



  # -------------------------------------------------------------------------
  #
  # execute_command
  #
  # -------------------------------------------------------------------------
  def execute_command(self, command):
    """ This method run a command as a subprocess. Typical use case is
    running commands.

    This method is a wrapper to subprocess.run , and will be moved soon
    in a helper object. It provides mutalisation of error handling
    """

    self.project.logging.debug("running : " + command)

    try:
      # Execute the subprocess, output ans errors are piped
      completed = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 shell=True, check=True, universal_newlines=False)

      # Return the output of the process to the caller
      return completed.stdout

    except subprocess.CalledProcessError as exception:
      self.cleanup()
      self.project.logging.critical("Error %d occured when executing %s",
                                    exception.returncode, exception.cmd)
      self.project.logging.debug("stdout was :")
      self.project.logging.debug(exception.stdout)
      self.project.logging.debug("stderr was :")
      self.project.logging.debug(exception.stderr)
      exit(1)


  # -------------------------------------------------------------------------
  #
  # setup_qemu
  #
  # -------------------------------------------------------------------------
  def setup_qemu(self):
    """This method remove the QEMU static binary which has been previously
    copied to the target
    """

    # We should not execute if the flag is not set. Should have already
    # been tested, but double check by security
    if self.use_qemu_static != True:
      return

    # Copy the QEMU binary to the target, using root privileges
    if   self.project.get_target_arch() == "armhf":
      qemu_target_arch = "arm"
    elif self.project.get_target_arch() == "armel":
      qemu_target_arch = "arm"
    elif self.project.get_target_arch() == "arm64":
      qemu_target_arch = "aarch64"
    else:
      qemu_target_arch = self.project.get_target_arch()

    # qemu (static) has not a consistent naming among distributions. Gentoo
    # will name it 'qemu-ARCH' whereas debian will name it 'qemu-ARCH-static".
    qemu_candidates = [
        "/usr/bin/qemu-" + qemu_target_arch,
        "/usr/bin/qemu-" + qemu_target_arch + "-static"
    ]
    for qemu in qemu_candidates:
      # We first check that the candidate file exists
      if os.path.exists(qemu):
        # Then, we run the file command to check whether the qemu program is
        # statically linked or not. If this is true, we use this program as
        # the qemu-static for the target architecture.
        output = subprocess.check_output(["file", "--brief", "-L", qemu])
        # The output of file will be something like:
        # <type>, <arch>, <version>, <link type>, <interpreter>,  [...]
        # and we are interested in the 4th parameter (link type).
        link_info = output.decode(Key.UTF8.value).split(", ")[3]
        if link_info == "statically linked":
          self.qemu_binary = qemu
          break # Found, stop iterating.

    # Check that a valid qemu binary was found in the previous step
    if not self.qemu_binary:
      self.project.logging.critical("Failed to find qemu (static) for %s",
                                    qemu_target_arch)
      exit(1)

    # Generate the qemu binary name

    self.project.logging.info("setting up QEMU for arch " + self.project.get_target_arch() +
                              " (using " + self.qemu_binary + ")")
    command = "cp " + self.qemu_binary + " "
    command += self.project.get_rootfs_mountpoint() + "/usr/bin/"
    self.execute_command(command)


  # -------------------------------------------------------------------------
  #
  # cleanup_qemu
  #
  # -------------------------------------------------------------------------
  def cleanup_qemu(self):
    """This method copy the QEMU static binary to the target
    """

    # We should not execute if the flag is not set. Should have already
    # been tested, but double check by security
    if self.use_qemu_static != True:
      return

    if self.project.dft.keep_bootstrap_files:
      self.project.logging.debug("keep_bootstrap_files is activated, keeping QEMU in " +
                                 self.project.get_rootfs_mountpoint())
      return

    # Remove he QEmu binary if it exist
    self.project.logging.info("cleaning QEMU for arch " + self.project.get_target_arch() +
                              "(using " + self.qemu_binary +")")
    try:
      os.remove(self.project.get_rootfs_mountpoint() + self.qemu_binary)

    # Catch OSError in case of file removal error
    except OSError as err:
      # If file does not exit errno value will be ENOENT
      if err.errno != errno.ENOENT:
        # Thus if exception was caused by something else, throw it upward
        raise

    # Empty the binary name
    self.qemu_binary = None



  # -------------------------------------------------------------------------
  #
  # remove_package
  #
  # -------------------------------------------------------------------------
  def remove_package(self, target):
    """This method deinstall a package or a list of packages from the target
    rootfs, and purge its configuration file. It will remove anything
    necessary to prevent having packages in the 'rc' state.

    This command is executed inside the chrooted environment and may need to
    have qemu installed.
    """

    self.project.logging.debug("Remove package : " + target)
    command = "chroot " + self.project.get_rootfs_mountpoint()
    command += " /usr/bin/apt-get autoremove --purge --yes " + target
    self.execute_command(command)


  # -------------------------------------------------------------------------
  #
  # install_package
  #
  # -------------------------------------------------------------------------
  def install_package(self, target):
    """This method install a package or a list of packages into the target
    rootfs.

    This command is executed inside the chrooted environment and may need to
    have qemu installed.
    """

    self.project.logging.debug("Install package(s) : " + target)
    command = "chroot " + self.project.get_rootfs_mountpoint()
    command += " /usr/bin/apt-get install --no-install-recommends --yes "
    command += " --allow-unauthenticated  " + target
    self.execute_command(command)



  # -------------------------------------------------------------------------
  #
  # add_catalog_signing_key
  #
  # -------------------------------------------------------------------------
  def add_catalog_signing_key(self, key):
    """This method add a new signing key to the list of known keys.
    """

#TODO keyserver should be a configuration value
    command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
    command += " apt-key adv --recv-keys --keyserver keyserver.ubuntu.com " + key
    self.execute_command(command)

    # Import the key into GnuPG - It has to be done in three step because
    # the apt-key recv does not work without a terminal and a stdout
#    command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
#    command += " gpg --homedir=/tmp --keyserver keyserver.ubuntu.com --recv " + key
#    self.execute_command(command)

    # Export the key to a temporary file
#    key_file = "/tmp/temp_keyserver.ubuntu.com_" + key
#    command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
#    command += " gpg --homedir=/tmp --export --armor " + key + " > " + key_file
#    self.execute_command(command)

#    command = "LANG=C chroot " + self.project.get_rootfs_mountpoint()
#    command += " apt-key add  " + key_file
#    self.execute_command(command)

    # Finally remove the temporary file
#    os.remove(self.project.get_rootfs_mountpoint() + key_file)

# TODO remove the imported pubkey from gnupg

  # -------------------------------------------------------------------------
  #
  # update_package_catalog
  #
  # -------------------------------------------------------------------------
  def update_package_catalog(self):
    """This method updates the local catalog using the remote server defined
    in /etc/apt/sources.list.

    This command is executed inside the chrooted environment and may need to
    have qemu installed.
    """

    self.project.logging.debug("Updating APT catalog")
    command = "chroot " + self.project.get_rootfs_mountpoint()
    command += " /usr/bin/apt-get update --yes --allow-unauthenticated "
    self.execute_command(command)



  # -------------------------------------------------------------------------
  #
  # upgrade_packages
  #
  # -------------------------------------------------------------------------
  def upgrade_packages(self, allow_downgrades=False):
    """This method runs a full upgrade inside the local chroot.

    This command is executed inside the chrooted environment and may need to
    have qemu installed.
    """

    self.project.logging.debug("Upgrading packages")
    command = "chroot " + self.project.get_rootfs_mountpoint()
    command += " /usr/bin/apt full-upgrade --yes"

    # Check if the allow downgrades flag is set
    if allow_downgrades:
      command += " --allow-downgrades "

    self.execute_command(command)



  # -------------------------------------------------------------------------
  #
  # setup_chrooted_environment
  #
  # -------------------------------------------------------------------------
  def setup_chrooted_environment(self):
    """This method mount in the chrooted environment all of the special
    filesystems needed to make application work properly once chrooted.
    """

    # Mount bind /proc into the rootfs mountpoint
    command = "mount --bind --make-rslave /proc " + self.project.get_rootfs_mountpoint()
    command += "/proc"
    self.execute_command(command)
    self.proc_is_mounted = True

    # Mount bind /dev/pts into the rootfs mountpoint
    command = "mount --bind --make-rslave /dev/pts "
    command += self.project.get_rootfs_mountpoint() + "/dev/pts"
    self.execute_command(command)
    self.devpts_is_mounted = True

    # Mount bind /dev/shm into the rootfs mountpoint
    command = "mount --bind --make-rslave /dev/shm "
    command += self.project.get_rootfs_mountpoint() + "/dev/shm"
    self.execute_command(command)
    self.devshm_is_mounted = True



  # -------------------------------------------------------------------------
  #
  # teardown_chrooted_environment
  #
  # -------------------------------------------------------------------------
  def teardown_chrooted_environment(self):
    """This method umount in the chrooted environment all of the special
    filesystems needed to make application work properly once chrooted.
    """

    # Are we already doing a cleanup ? this may happens if an exception
    # occurs when cleaning up. It prevents multiple call and loop in
    # exception processing
    if self.cleanup_in_progress:
      return

    # Set the flag used to prevent multiple call
    self.cleanup_in_progress = True

    # Check if /proc is mounted, then umount it
    if self.proc_is_mounted:
      command = "umount " + self.project.get_rootfs_mountpoint() + "/dev/pts"
      self.execute_command(command)
      self.proc_is_mounted = False

    # Check if /dev/shm is mounted, then umount it
    if self.devshm_is_mounted:
      command = "umount " + self.project.get_rootfs_mountpoint() + "/dev/shm"
      self.execute_command(command)
      self.devshm_is_mounted = False

    # Check if /dev/pts is mounted, then umount it
    if self.devpts_is_mounted:
      command = "umount " + self.project.get_rootfs_mountpoint() + "/proc"
      self.execute_command(command)
      self.devpts_is_mounted = False

    self.cleanup_in_progress = False



  # -------------------------------------------------------------------------
  #
  # output_string_with_result
  #
  # -------------------------------------------------------------------------
  def output_string_with_result(self, msg, code):
    """ This method output a string followed by a result code. Resultat code
    is an enumed value. Color depends on code value:
      . OK      => Green
      . Warning => Orange
      . KO      => Red

    Result codes are right aligned to a value defined in this class members
    at init.
    """

    # Let's build the output string with padding and ANSI code for colors.
    # First the string fragment with ANSI codes
    str_code = "["

    # Complete with color according to the code
    if code == Code.SUCCESS:
      str_code += Colors.FG_GREEN.value
    elif code == Code.FAILURE:
      str_code += Colors.FG_RED.value
    if code == Code.WARNING:
      str_code += Colors.FG_ORANGE.value

    # Add bold, value, then go back to normal output
    str_code += Colors.BOLD.value + code.value + Colors.RESET.value + "]"

    # if the string is wider than alignment valuem then result code will be
    # on a new line. An extra 8 chars are remove from
    output = msg

    # We cannot use len(str_code) since it includes ANSI codes which are not printable
    # Instead we use the code_size constant which is the number of actual char printed
    if len(output) >= (self.right_align - self.len_str_code):
      output += "\n"
      output += "".join(" " for i in range(self.right_align - self.len_str_code))
    else:
      output += "".join(" " for i in range(self.right_align - len(output) - self.len_str_code))

    # Last thing to do is to concatenate the string with code and colors
    output += str_code
    output = str_code + " " + msg

    # And print it !
    print(output)


  # -------------------------------------------------------------------------
  #
  # display_test_result
  #
  # -------------------------------------------------------------------------
  def display_test_result(self, msg, target=Output.STDOUT):
    """ This method output a string either to stdout or log according to
    arguments. String is prefixed by the Hint keyword and is targetting
    hint's to explain why a test has failed.
    """

    # First add some padding since code are left aligned
    output = "".join(" " for i in range(self.len_str_code + 1))

    # Complete with color according to the code
    if target == Output.STDOUT:
      output += Colors.FG_CYAN.value
      output += Colors.BOLD.value + "Hint: " + Colors.RESET.value

    # if the string is wider than alignment valuem then result code will be
    # on a new line. An extra 8 chars are remove from
    output += msg

    # And print it !
    if target == Output.STDOUT:
      print(output)
    else:
      self.project.logging.log(output.value, output)

  # -------------------------------------------------------------------------
  #
  # setup_kernel_apt_sources
  #
  # -------------------------------------------------------------------------
  def setup_kernel_apt_sources(self, target, version):
    """This method implement the installation of the bootchain in the
    generated rootfs. The bootchain inludes the kernel itself, uboot,
    dtb files etc.
    """

    # Output current task to logs
    logging.info("Setting up APT sources for kernel")

    # Generated the base path to the file to create
    filepath = self.project.get_rootfs_mountpoint() + "/etc/apt/sources.list.d/"

    # Control the package provider. So far only handles debian armbian and devuan
    if target[Key.ORIGIN.value] not in "devuan" "debian" "armbian" "armwizard" "custom":
      logging.error("Unknown kernel provider '" + target[Key.ORIGIN.value] + "'")
      exit(1)

    # Check if the provider is Debian, if yes, there is nothing to do for source list generation
    # The system will use the sources defined for rootfs installation
    if target[Key.ORIGIN.value] == Key.DEBIAN.value:
      logging.debug("Using Debian repo as source provider.")
    else:
      # Set the repo name to None. It will be checked in the end to know if there is a key
      # to install (key may have be installed using wget instead of apt-key in case of custom repo)
      repo_pub_key = None

      # Target is not Debian, then we need to create a temporary file for source file generation
      # and complete the path according to the known providers
      with tempfile.NamedTemporaryFile(mode='w+', delete=False) as working_file:
        if target[Key.ORIGIN.value] == Key.DEVUAN.value:
          # Defines the file name and content for devuan APT sources
          logging.debug("Using Devuan repo as source provider. Adding devuan.list")
          filepath += "devuan_repository.list"
          working_file.write("deb http://packages.devuan.org/devuan ")
          working_file.write(target[Key.VERSION.value])
          working_file.write(" main\n")

          # Check if the public key of the repository is defined in the BSP file, otherwise
          # Set the default value of the key
          if Key.PUBKEY.value not in target:
            repo_pub_key = Key.DEVUAN_SIGNING_PUBKEY.value
            logging.debug("Using default Devuan signing key " + repo_pub_key)
          else:
            repo_pub_key = target[Key.PUBKEY.value]
            logging.debug("Add Devuan signing key " + repo_pub_key)

        elif target[Key.ORIGIN.value] == Key.ARMBIAN.value:
          # Defines the file name and content for armbian APT sources
          logging.debug("Using Armbian repo as source provider. Adding armbian.list")
          filepath += "armbian_repository.list"
          working_file.write("deb http://apt.armbian.com jessie main utils jessie-desktop\n")

          # Check if the public key of the repository is defined in the BSP file, otherwise
          # Set the default value of the key
          if Key.PUBKEY.value not in target:
            repo_pub_key = Key.ARMBIAN_SIGNING_PUBKEY.value
            logging.debug("Using default Armbian signing key " + repo_pub_key)
          else:
            repo_pub_key = target[Key.PUBKEY.value]
            logging.debug("Add Armbian signing key " + repo_pub_key)

        elif target[Key.ORIGIN.value] == Key.ARMWIZARD.value:
          # Defines the file name and content for armbian APT sources
          logging.debug("Using ArmWizard repo as source provider. Adding armwizard.list")
          filepath += "armwizard_repository.list"
          working_file.write("deb http://apt.armwizard.org/armwizard " + version)
          working_file.write(" bsp\n")

          # Check if the public key of the repository is defined in the BSP file, otherwise
          # Set the default value of the key
          if Key.PUBKEY.value not in target:
            repo_pub_key = Key.ARMWIZARD_SIGNING_PUBKEY.value
            logging.debug("Using default Armwizard signing key " + repo_pub_key)
          else:
            repo_pub_key = target[Key.PUBKEY.value]
            logging.debug("Add Armbian signing key " + repo_pub_key)

        elif target[Key.ORIGIN.value] == Key.CUSTOM.value:
          # Defines the file name and content for custom APT sources
          logging.debug("Using custom repo as source provider. Adding custom_bsp_repository.list")
          filepath += "custom_bsp_repository.list"
          working_file.write("deb " + target[Key.URL.value] + "\n")

          # Check if the public key of the repository is defined in the BSP file, otherwise
          # Check if there is a pubkey to retrieve using its url
          if Key.PUBKEY_URL.value in target:
            key_url = target[Key.PUBKEY_URL.value]
            logging.debug("retrieving public key : " + key_url)

            # Generate the retrieve and add command
            command = "chroot " + self.project.get_rootfs_mountpoint() + " bash -c "
            command += "'/usr/bin/wget -qO - "
            command += target[Key.PUBKEY_URL.value]
            command += " | /usr/bin/apt-key add -'"
            self.execute_command(command)

          # Public key is not available, installation is likely to fail
          else:
            logging.error("No public key is defined in board definition.")
            logging.error("Continuing, but installation of kernel is likely to fail.")

      # Update new source file permissions. It has to be world readable
      os.chmod(working_file.name, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)

      # Move the temporary file under the rootfs tree
      command = "mv -f " + working_file.name + " " + filepath
      self.execute_command(command)

      # Add a key to the know catalog signing keys, only if a key fingerprint has been defined
      if not repo_pub_key is None:
        self.add_catalog_signing_key(repo_pub_key)

      # Update the catalog once the new sources is set
      self.update_package_catalog()


  # -------------------------------------------------------------------------
  #
  # install_kernel_apt_packages
  #
  # -------------------------------------------------------------------------
  def install_kernel_apt_packages(self, target):
    """This method implement the installation of the bootchain in the
    generated rootfs. The bootchain inludes the kernel itself, uboot,
    dtb files etc.
    """

    # Output current task to logs
    logging.info("Installing kernel packages")

    # Check that the packages list is defined under kernel entry
    if Key.PACKAGES.value in target:
      # Iterate the list of packages to install, and install them
      for pkg in target[Key.PACKAGES.value]:
        logging.debug("Installing package " + pkg)
        self.install_package(pkg)
    else:
      logging.debug("No packages entry found. Nothing to do...")


  # -------------------------------------------------------------------------
  #
  # umount_mountpoint
  #
  # -------------------------------------------------------------------------
  def umount_mountpoint(self, target):
    """This method make the call to the umount system utilities. It controls
    that the mountpoint exist and is mounted before calling the umount command
    """

    # Output current task to logs
    logging.debug("Umounting " + target)

    # TODO check mount point exist
    # TODO check that mount point is mounted

    # Generate the umount command and execute it
    command = 'umount "' + target + '"'
    self.execute_command(command)

  # -------------------------------------------------------------------------
  #
  # cleanup
  #
  # -------------------------------------------------------------------------
  def cleanup(self):
    """This method is in charge of cleaning the environment in case of errors.
    It should not be called from here but from children classes.
    """
    self.project.logging.critical("Should not be called from parent class !")
