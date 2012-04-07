ZFS InitramFS Creator
Jonathan Vasquez
Version 1.0.0
Distributed under GPLv2

This script generates an initramfs image with all the included files and dependencies.

You will need a few programs already installed on your computer since this script just automates
the process of you actually going into your filesystem, and getting all those files.

Please have the following installed:

- Kernel
- SPL
- ZFS with static-libs flag
- Busybox with static flag
- cpio

I can't remember any other apps atm. Also make sure you have a supporting bootloader. I'm using GRUB 2.00~beta3.

This script and applications have been tested only on Gentoo Linux. It should work in other linuxes as well.