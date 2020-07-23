## Bliss Initramfs

A fork with the primary goal of keeping full LUKS + ZFS support.
Originally 
[fearedbliss/bliss-initramfs](https://github.com/fearedbliss/bliss-initramfs)
by Jonathan Vasquez, designed for Gentoo Linux.

## Description

An utility that generates an initramfs image with all files and dependencies
needed to boot your Gentoo Linux system installed on OpenZFS. This program was
designed as a simple alternative to genkernel for this use case.

## Usage

All you need to do is run the utility, select the options you want "a-la-carte",
and then tell the initramfs via your bootloader parameters in what order you
want those features to be trigered in. Check the USAGE file for examples.

## License

Released under the Apache License 2.0

## Dependencies

Please have the following installed:

- dev-lang/python 3.6+
- app-arch/cpio
- app-shells/bash
- sys-apps/kmod
- sys-apps/grep
- sys-fs/udev OR sys-fs/eudev OR sys-apps/systemd (UUIDs, Labels, etc)
- sys-apps/kbd (Keymap support)
- sys-fs/zfs (ZFS support)
- sys-fs/cryptsetup (LUKS support)
- app-crypt/gnupg (GPG Encrypted Keyfile used for LUKS)
- app-arch/gzip (initramfs compression)

For more information/instructions check the USAGE file.

## Contributions

Before submitting a patch, make sure to run `black` on the code.