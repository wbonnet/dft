Rootfs
======

Purpose
-------

This folder is part of the DFT configuration library. It contains multiple files defining
frequently used rootfs.

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
