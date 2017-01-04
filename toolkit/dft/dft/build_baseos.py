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

import logging, os, subprocess, tarfile, shutil, tempfile, distutils
from distutils import dir_util, file_util
from cli_command import CliCommand

#
#    Class BuildBaseOS
#
class BuildBaseOS(CliCommand): 
    """This class implements method needed to create the base OS

       The "base OS" is the initial installation of Debian (debootstrap) which
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
        super().__init__(dft, project)

        # Set the log level from the configuration
        logging.basicConfig(level=project.dft.log_level)

    # -------------------------------------------------------------------------
    #
    # install_baseos
    #
    # -------------------------------------------------------------------------
    def install_baseos(self):
        """This method implement the business logic of generating the rootfs.
        It calls dedicated method for each step. The main steps are :

        . setting up working directory
        . extracting cache archive content or running debootstrap
        . setup QEMU and run stage 2 if needed
        . update cache if needed
        . deploy DFT Ansible templates, and run Ansible to do confiugration
        . cleanup installation files
        . cleanup QEMU if needed
        """

        # Check that DFT path is valid
        if os.path.isdir(self.project.project_definition["configuration"]["dft_base"]) == False:
            logging.critical("Path to DFT installation is not valid : %s",  self.project.project_definition["configuration"]["dft_base"])
            exit(1)

        # Ensure target rootfs mountpoint exists and is a dir
        if os.path.isdir(self.project.rootfs_mountpoint) == False:
            os.makedirs(self.project.rootfs_mountpoint)
        else:
            if "keep_rootfs_history" in self.project.project_definition["configuration"] and self.project.project_definition["configuration"]["keep_rootfs_history"] == True:
                logging.warn("target rootfs mount point already exists : " + self.project.rootfs_mountpoint)
# TODO
                logging.critical("TODO : handle history : " + self.project.rootfs_mountpoint)
                exit(1)
# It looks like i need to add a symlink from history to current
# It should be optional with overwrite on factory_setup_definition
# Depending on keeping history or not. So far not available
# default behavior is not to keep history
            else:

# TODO security hole !!!!!
# Protect path generation to avoid to remove / !!!
                sudo_command = 'sudo rm -fr "' + self.project.rootfs_mountpoint +'"'
                self.execute_command(sudo_command)
                os.makedirs(self.project.rootfs_mountpoint)

        # Check if the archive has to be used instead of doing a debootstraping
        # for real. Only if the archive exist...
        if self.project.dft.use_cache_archive == True and self.cache_archive_is_available == True:
            self.fake_generate_debootstrap_rootfs()
        else:
            # In any other cases, do a real debootstrap call
            self.generate_debootstrap_rootfs()

        # Test if the archive has to be updated
        if self.project.dft.update_cache_archive == True:
            # But only do it if we haven't bee using the cache, or it
            # would be extracted, then archived again.
            if self.project.dft.use_cache_archive == True:
                self.update_rootfs_archive()

        # Launch Ansible to install roles identified in configuration file
        self.install_packages()

        # Once installation has been played, we need to do some cleanup
        # like ensute that no mount bind is still mounted, or delete the
        # DFT ansible files
        self.cleanup_installation_files()

        # Remove QEMU if it has been isntalled. It has to be done in the end
        # since some cleanup tasks could need QEMU
        if self.use_qemu_static == True:
            self.cleanup_qemu()



    # -------------------------------------------------------------------------
    #
    # install_packages
    #
    # -------------------------------------------------------------------------
    def install_packages(self):
        """This method remove the QEMU static binary which has been previously 
        copied to the target 
        """

        logging.info("installing packages...")

        # Create the target directory. DFT files will be installed under this
        # directory.
        try:
            logging.debug("copying DFT toolkit...")

            # Create the target directory in the rootfs
            dft_target_path = self.project.rootfs_mountpoint + "/dft_bootstrap/"
            if not os.path.exists(dft_target_path):
                os.makedirs(dft_target_path)

            # Copy the DFT toolkit content to the target rootfs
            for target_to_copy in os.listdir(self.project.project_definition["configuration"]["dft_base"]):
                logging.debug("Copy the DFT toolkit : preparing to copy " + target_to_copy)
                target_to_copy_path = os.path.join(self.project.project_definition["configuration"]["dft_base"], target_to_copy)
                if os.path.isfile(target_to_copy_path):
                    logging.debug("copying file " + target_to_copy_path + " => " + dft_target_path)
                    distutils.file_util.copy_file(target_to_copy_path, dft_target_path)
                else:
                    logging.debug("copying tree " + target_to_copy_path + " => " + dft_target_path)
                    distutils.dir_util.copy_tree(target_to_copy_path, os.path.join(dft_target_path, target_to_copy))

            # Copy the additional toolkit content to the target rootfs
            if "additional_roles" in self.project.project_definition["configuration"]:
                for additional_path in self.project.project_definition["configuration"]["additional_roles"]:
                    logging.debug("Copy the additional toolkit : preparing to copy from additional path " + additional_path)
                    for target_to_copy in os.listdir(additional_path):
                        logging.debug("Copy the additional toolkit : preparing to copy " + target_to_copy)
                        target_to_copy_path = os.path.join(additional_path, target_to_copy)
                        if os.path.isfile(target_to_copy_path):
                            logging.debug("copying file " + target_to_copy_path + " => " + dft_target_path)
                            distutils.file_util.copy_file(target_to_copy_path, dft_target_path)
                        else:
                            logging.debug("copying tree " + target_to_copy_path + " => " + dft_target_path)
                            distutils.dir_util.copy_tree(target_to_copy_path, os.path.join(dft_target_path, target_to_copy))

        except OSError as e:
            # Call clean up to umount /proc and /dev
            self.cleanup_installation_files()
            logging.critical("Error: %s - %s." % (e.filename, e.strerror))
            exit(1)

        except shutil.Error as e:
            self.cleanup_installation_files()
            logging.critical("Error: %s - %s." % (e.filename, e.strerror))
            exit(1)

        # Flag if someroles has been foundand added to site.yml
        role_has_been_found = False
     
        # Generate the site file including all the roles from baseos 
        # configuration, then move  roles to the target rootfs
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            # Generate file header
            f.write("# Defines the role associated to the rootfs being generated\n")
            f.write("---\n")
            f.write("- hosts: local\n")
            f.write("  roles:\n")

            # Iterate the list of distributions loaded from the file
            for role in self.project.baseos_definition["roles"]:
                # At least one role has beenfound, flag it
                role_has_been_found = True
                logging.debug("Adding role " + role)               
                f.write("  - " + role + "\n")
        f.close()

        # Generate the file path
        filepath = self.project.rootfs_mountpoint + "/dft_bootstrap/site.yml"

        # Finally move the temporary file under the rootfs tree
        sudo_command = "sudo mv -f " + f.name + " " + filepath
        self.execute_command(sudo_command)

        # Warn the user if no role is found. In such case baseos will be same
        # debotstrap, which is certainly not what is expected
        if role_has_been_found == False:
            logging.warning("No role has been found in baseos definiion. Rootfs is same as debootstrap output")
            logging.error("You may wish to have a look to : " + self.project.genereate_definition_file_path(self.project.project_definition["project-definition"]["baseos"][0]) )

        # Execute Ansible
        # TODO : multiple target ? not sure...
        logging.info("running ansible...")
        sudo_command = "LANG=C sudo chroot " + self.project.rootfs_mountpoint + " /bin/bash -c \"cd /dft_bootstrap && /usr/bin/ansible-playbook -i inventory.yml -c local site.yml\""
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

        logging.info("starting to generate build number")

        # Open the file and writes the timestamp in it
        filepath = self.project.rootfs_mountpoint + "/etc/dft_version"
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            f.write("DFT-" + self.project.timestamp + "\n")
        f.close()

        sudo_command = "sudo mv -f " + f.name + " " + filepath
        self.execute_command(sudo_command)


    # -------------------------------------------------------------------------
    #
    # update_rootfs_archive
    #
    # -------------------------------------------------------------------------
    def update_rootfs_archive(self):
        """This methods update (delete then recreate) the rootfs archive after
        doing a real debootstrap installation.

        Archive is not updated if cache has been used instead of debootstraping
        otherwise it would generate the same archive"""
        logging.info("starting to update rootfs archive")

        # Remove existing archive before generating the new one
        try:
            if os.path.isfile(self.project.archive_filename) == True:
                logging.info("removing previous archive file : " + self.project.archive_filename)
                os.remove(self.project.archive_filename)

        # Catch file removal exceptions
        except OSError as e:
            logging.critical("Error: %s - %s." % (e.filename, e.strerror))
            self.cleanup_installation_files()
            exit(1)

        # Create the new archive
        cache_archive = tarfile.open(self.project.archive_filename)
        cache_archive.add(name=self.project.rootfs_mountpoint)
        cache_archive.close()



    # -------------------------------------------------------------------------
    #
    # fake_generate_debootstrap_rootfs
    #
    # -------------------------------------------------------------------------
    def fake_generate_debootstrap_rootfs(self):
        logging.info("starting to fake generate debootstrap rootfs")

        # Check that the archive exists
        if os.path.isfile(self.project.archive_filename) == False:
            logging.warning("cache has been activate and archive file does not exist : " + self.archive_filename)
            return False

        # Extract tar file to rootfs mountpoint
        logging.info("extracting archive : " + self.project.archive_filename)
        cache_archive = tarfile.open(self.project.archive_filename)
        cache_archive.extractall(path=self.project.rootfs_mountpoint)
        cache_archive.close()



    # -------------------------------------------------------------------------
    #
    # generate_debootstrap_rootfs
    #
    # -------------------------------------------------------------------------
    def generate_debootstrap_rootfs(self):
        """
        """

        logging.info("starting to generate debootstrap rootfs")

        # Generate the base debootstrap command
        debootstrap_command  = "sudo debootstrap --no-check-gpg"

        # Add the foreign and arch only if they are different from host, and
        # thus if use_qemu_static is True
        if self.use_qemu_static == True:
            logging.info("running debootstrap stage 1")
            debootstrap_command += " --foreign --arch=" + self.project.target_arch 
        else:
            logging.info("running debootstrap")

        # Add the target, mount point and repository url to the debootstrap command
        debootstrap_command += " " +  self.project.target_version + " " + self.project.rootfs_mountpoint + " " + self.project.project_definition["project-definition"]["debootstrap-repository"]

        # Finally run the subprocess
        self.execute_command(debootstrap_command)

        # Check if we are working with foreign arch, then ... 
        if self.use_qemu_static == True:
            # QEMU is used, and we have to install it into the target
            self.setup_qemu()

            # And second stage must be run
            logging.info("doing debootstrap stage 2")
            debootstrap_command  = "LANG=C sudo chroot " + self.project.rootfs_mountpoint + " /debootstrap/debootstrap --second-stage"
            self.execute_command(debootstrap_command)


        # Mount bind /proc into the rootfs mountpoint
        sudo_command = "sudo mount --bind --make-rslave /proc " + self.project.rootfs_mountpoint + "/proc"
        self.execute_command(sudo_command)
        self.proc_is_mounted = True

        # Mount bind /dev/pts into the rootfs mountpoint
        sudo_command = "sudo mount --bind --make-rslave /dev/pts " + self.project.rootfs_mountpoint + "/dev/pts"
        self.execute_command(sudo_command)
        self.devpts_is_mounted = True

        # Mount bind /dev/shm into the rootfs mountpoint
        sudo_command = "sudo mount --bind --make-rslave /dev/shm " + self.project.rootfs_mountpoint + "/dev/shm"
        self.execute_command(sudo_command)
        self.devshm_is_mounted = True

        # Update the APT sources
        self.generate_apt_sources_configuration()

        # Then update the list of packages
        apt_command = "sudo chroot " + self.project.rootfs_mountpoint + " /usr/bin/apt-get update"
        self.execute_command(apt_command)
 
        # Install extra packages into the chroot
        apt_command = "sudo chroot " + self.project.rootfs_mountpoint + " /usr/bin/apt-get install --no-install-recommends --yes --allow-unauthenticated apt-utils ansible"
        self.execute_command(apt_command)

        # Generate a unique build timestamp into /etc/dft_version 
        self.generate_build_number()



    # -------------------------------------------------------------------------
    #
    # generate_apt_sources_configuration
    #
    # -------------------------------------------------------------------------
    def generate_apt_sources_configuration(self):
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
#TODO : remove validity check after generation ? => flag ? 
        logging.info("starting to generate APT sources configuration")

        # Generate the file path
        filepath = self.project.rootfs_mountpoint + "/etc/apt/apt.conf.d/10no-check-valid-until"

        # Open the file and writes configuration in it
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            f.write("Acquire::Check-Valid-Until \"0\";\n")
        f.close()

        sudo_command = "sudo mv -f " + f.name + " " + filepath
        self.execute_command(sudo_command)

        # Generate the file path
        filepath = self.project.rootfs_mountpoint + "/etc/apt/sources.list"

        # Open the file and writes configuration in it
        self.project.debian_mirror_url = self.project.project_definition["project-definition"]["debootstrap-repository"]

        # Flag if we have found a matching distro or not
        distro_has_been_found = False

        # The open the temp file for output, and iterate the distro dictionnary
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            # Iterate the list of distributions loaded from the file
            for distro in self.project.repositories_definition["distributions"]:
                logging.debug(distro)
                # Process only if it is the version we target
                if distro["name"]== self.project.target_version and self.project.target_arch in distro["architectures"]:
                    # W have found a matching distro or not
                    distro_has_been_found = True
                    # Then iterate all the sources for this distro version
                    for repo in distro["repositories"]:
                        logging.debug(repo)
                        # Generate the line in the sources.list file
                        f.write("deb " + repo["url"] +" " + repo["suite"] + " ")                    
                        for section in repo["sections"]:
                            f.write(section + " ")                    
                        f.write("\n")           

        # Warn the user if no matching distro is found. There will be an empty
        # /etc/apt/sources.list and installation will faill
        if distro_has_been_found == False:
            self.cleanup_installation_files()
            logging.error("No distribution matching " + self.project.target_version + " has been found.")
            logging.error("Please check repositories definition for this project." )
            logging.error("File in use is : " + self.project.genereate_definition_file_path(self.project.project_definition["project-definition"]["repositories"][0]) )
            logging.critical("Cannot generate /etc/apt/sources.list under rootfs path. Operation is aborted !" )
            exit(1)
 
# TODO : generate deb-src ? not really sure... optionnal ?                   
        f.close()

        # Finally move the temporary file under the rootfs tree
        sudo_command = "sudo mv -f " + f.name + " " + filepath
        self.execute_command(sudo_command)
