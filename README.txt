ZFS InitramFS Creator
Jonathan Vasquez
Version 1.2
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

Changes since 1.0.0
-------------------
- Cleaned up code
- Added checks to make sure all the files exist and are being added
- Script is now parameter based. You no longer have to open up the file to add
  your kernel name. Just pass the name of your kernel and zfs pool name to the
  script. ./createInit <Kernel Name> <ZFS Pool Name>
- You no longer need to edit the init script since the createInit script now
  uses your parameters and sed to do the appropriate changes to the init file.
- Files added are now verbose (You will see what is happening)
- More variables are now available to make it easy for distros with different
binary file placements to use this script. This makes the entire script much
more flexible and modular.
- Added help screen with -h
