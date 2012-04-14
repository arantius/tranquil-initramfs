ZFS InitramFS Creator
Jonathan Vasquez
Version 1.0.1-next
Distributed under GPLv2

This script generates an initramfs image with all the included files and dependencies.

You will need a few programs already installed on your computer since this script just automates
the process of you actually going into your filesystem, and getting all those files.

Please have the following installed:

- Linux Kernel with CONFIG_PREEMPT, CONFIG_PREEMPT_VOLUNTARY disabled, and ZLIB_INFLATE, ZLIB_DEFLATE enabled.
- SPL
- ZFS 
- Busybox with static flag
- cpio
- GRUB 2.00_beta3 or later, or a bootloader that supports ZFS.

This script and applications have been tested only on Gentoo Linux. It should
work on other distros as well.
