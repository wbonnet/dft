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
#    Class BuildFirmware
#
class BuildFirmware(CliCommand): 
    """This class implements method needed to create the squashfs file(s) used
    to storefirmware content
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

    # -------------------------------------------------------------------------
    #
    # build_firmware
    #
    # -------------------------------------------------------------------------
    def build_firmware(self):
        """This method implement the business logic of firmware generation.
        Firmware is  squashfs file containing the rootfs generated previoulsy. 
        
        It calls dedicated method for each step. The main steps are :

        . 
        """

        # Ensure firmware generation path exists and is a dir
        if os.path.isdir(self.project.squashfs_target_directory) == False:
            os.makedirs(self.project.squashfs_target_directory)
        else:
#            sudo_command = 'sudo rm -fr "' + self.project.rootfs_mountpoint +'"'
 #           self.execute_command(sudo_command)
  #          os.makedirs(self.project.rootfs_mountpoint)


# TODO
# What is needed in the configuration file
# production:
# #   format: squashfs
# #   option...
# #   alternative to squashfs ? exploded maybe tarball with compression option
# #   target path ?

# # man mksquashfs

#    Filesystem build options
#        -comp COMPRESSION
#            select COMPRESSION compression. Compressors available: gzip  (default),
#            lzo, xz.

#        -b BLOCK_SIZE
#            set data block to BLOCK_SIZE. Default 131072 bytes.

#        -no-exports
#            don't make the filesystem exportable via NFS.

#        -no-sparse
#            don't detect sparse files.

#        -no-xattrs
#            don't store extended attributes.

#        -xattrs
#            store extended attributes (default).

#        -noI
#            do not compress inode table.

#        -noD
#            do not compress data blocks.

#        -noF
#            do not compress fragment blocks.

#        -noX
#            do not compress extended attributes.

#        -no-fragments
#            do not use fragments.

#        -always-use-fragments
#            use fragment blocks for files larger than block size.

#        -no-duplicates
#            do not perform duplicate checking.

#        -all-root
#            make all files owned by root.

#        -force-uid uid
#            set all file uids to uid.

#        -force-gid gid
#            set all file gids to gid.

#        -nopad
#            do not pad filesystem to a multiple of 4K.


#        -keep-as-directory
#            if  one source directory is specified, create a root directory contain‐
#            ing that directory, rather than the contents of the directory.

#    Filesystem filter options
#        -p PSEUDO_DEFINITION
#            Add pseudo file definition.

#        -pf PSEUDO_FILE
#            Add list of pseudo file definitions.

#        -sort SORT_FILE
#            sort files according to priorities in SORT_FILE. One file or  dir  with
#            priority per line. Priority -32768 to 32767, default priority 0.

#        -ef EXCLUDE_FILE
#            list of exclude dirs/files. One per line.

#        -wildcards
#            Allow  extended  shell  wildcards  (globbing)  to  be  used  in exclude
#            dirs/files

#        -regex
#            Allow POSIX regular expressions to be used in exclude dirs/files.

#    Filesystem append options
#        -noappend
#            do not append to existing filesystem.

#        -root-becomes NAME
#            when appending source files/directories, make the original root  become
#            a  subdirectory in the new root called NAME, rather than adding the new
#            source items to the original root.

#    Mksquashfs runtime options:
#        -version
#            print version, licence and copyright message.

#        -recover NAME
#            recover filesystem data using recovery file NAME.

#        -no-recovery
#            don't generate a recovery file.

#        -info
#            print files written to filesystem.

#        -no-progress
#            don't display the progress bar.

#        -processors NUMBER
#            Use NUMBER processors. By default will use number of processors  avail‐
#            able.

#        -read-queue SIZE
#            Set input queue to SIZE Mbytes. Default 64 Mbytes.

#        -write-queue SIZE
#            Set output queue to SIZE Mbytes. Default 512 Mbytes.

#        -fragment-queue SIZE
#            Set fragment queue to SIZE Mbytes. Default 64 Mbytes.

#    Miscellaneous options
#        -root-owned
#            alternative name for -all-root.

#        -noInodeCompression
#            alternative name for -noI.

#        -noDataCompression
#            alternative name for -noD.

#               -noFragmentCompression
#                    alternative name for -noF.

#                -noXattrCompression
#                    alternative name for -noX.

#            Compressors available and compressor specific options
#                gzip (no options) (default)

#                lzo (no options)

#                xz

#                -Xbcj filter1,filter2,...,filterN
#                    Compress  using  filter1,filter2,...,filterN in turn (in addition to no
#                    filter), and choose the best compression. Available filters: x86,  arm,
#                    armthumb, powerpc, sparc, ia64.

#                -Xdict-size DICT_SIZE
#                    Use  DICT_SIZE  as  the  XZ dictionary size. The dictionary size can be
#                    specified as a percentage of the block size, or as an  absolute  value.
#                    The  dictionary  size  must be less than or equal to the block size and
#                    8192 bytes or larger. It must also be storable  in  the  xz  header  as
#                    either  2^n  or as 2^n+2^(n+1). Example dict-sizes are 75%, 50%, 37.5%,
#                    25%, or 32K, 16K, 8K etc.


# Later add the possibility to generate several squashfs out of a baseos, and do delta, time based ? 

        logging.critical("Not yet available")
        exit(1)



