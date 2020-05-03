Rootfs
======

Purpose
-------

This folder contains element which are part of the DFT configuration library. There are multiple files
shared between images definitions such as roots content, disk image layout, official debian mirrors
and repositories definition configuration files. These items are frequently used by rootfs and
firmware images and thus shared. Project contains relative symlink.

These rootfs can be included in your project file (as long as you let library activated in
your configuration or project file).

Please keep in mind that a project can only contains one rootfs at a time. Thus multiple
includes are not possible.

Content
-------

The following rootfs are provided :

* Netshell : A simple rootfs providing a CLI system with OpenSSH running and DHCP (eth0)
*
*
