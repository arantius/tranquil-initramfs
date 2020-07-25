
## Tranquil Initramfs

A fork of
[fearedbliss/bliss-initramfs](https://github.com/fearedbliss/bliss-initramfs)
by Jonathan Vasquez, designed for Gentoo Linux.
The original goal is to keep full LUKS + ZFS support (removed in 9.0.0) and
avoid systemd by default (assumed after 8.0.0).

## Description

An utility that generates an initramfs image with all files and dependencies
needed to boot your Gentoo Linux system installed on OpenZFS. This program was
designed as a simple alternative to genkernel for this use case.

## Dependencies

For proper operation you'll need to have installed:

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

## Required Kernel Options

If configured as modules, these must be built into the initramfs.

### For Initramfs Support

    General setup --->
    > [*] Initial RAM filesystem and RAM disk (initramfs/initrd) support
      () Initramfs source file(s)

### For ZFS

    File systems --->
      [*] Miscellaneous filesystems  --->
        <*>   Persistent store support
        <*>     DEFLATE (ZLIB) compression

ZLIB_DEFLATE cannot be configured directly. "Persistent store support" is a
controllable option that sets it indirectly.  You can check the ZLIB_DEFLATE
dependencies (Do a search inside of menuconfig) to find other options

### For LUKS

    Device Drivers --->
    > Generic Driver Options --->
      [*] Maintain a devtmpfs filesystem to mount at /dev
      [*] Automount devtmpfs at /dev, after the kernel mounted the rootfs
    > [*] Multiple devices driver support (RAID and LVM) --->
      <*> Device mapper support
      <*> Crypt target support

    Cryptographic API --->
    * Any ciphers you need in order to unlock your encrypted drive should be
      enabled as either a module or built into the kernel.

## Usage

All you need to do is run the utility, select the options you want "a-la-carte",
and then tell the initramfs via your bootloader parameters in what order you
want those features to be trigered in.

### Creating the initramfs

Run the script with the command `./mkinitrd` .
If not run as root it will use `sudo` for the subprocesses which require it.

Select the features that you want, and tell it which kernel you want to use.

After that the required files will be gathered and packed into an initramfs and
you will find the initramfs in the directory that you are currently in. Copy
that file to your boot directory and name it whatever you want.

### Kernel Options

#### General

`root` - Location to rootfs
* example for ZFS: linux <kernel> root=tank/gentoo/root
* example for rootfs on luks partition: linux <kernel> root=/dev/mapper/vault_0
* example for regular drive: linux <kernel> root=/dev/sda4

`usr` - Location of separate /usr
* example: linux <kernel> root=/dev/sda4 usr=/dev/sda3

If you use this option, you need to make sure that /usr is on the same type of
style as your /. Meaning that if you have / in a ZFS dataset then /usr should be
on a ZFS dataset as well. You cannot have / on a ZFS dataset and /usr on a
regular partition. I don't foresee a scenario or a reason for why someone would
want to put their / on zfs and exclude their /usr from it. So this case should
be a rare one.

`recover` - Use this if you want the initrd to throw you into a rescue shell.
Useful for recovery and debugging purposes.
* example: linux \<kernel\> recover

`su` - Single User Mode. This is a really crappy implementation of a single user
mode. But at least it will help you if you forgot to change your password,
after installation.
* example: linux \<kernel\> root=tank/gentoo/root su

`init` - Specifies the init system to use. If the init system isn't located in
/sbin/init, you can specific it explictly:
* example: linux \<kernel\> root=tank/gentoo/root init=/path/to/init

`redetect` - Use this if you want to have the option to re-scan your /dev/
directory for new devices.

Sometimes during the output of available drives, you won't see your drives
listed, don't worry, if it normally works on your machine, your drive will
silently appear. You could just wait a few seconds yourself until you feel it is
ready, and then just press enter to attempt to mount and decrypt the drive.

triggers - Use this to let the initramfs load what feature hooks it needs to run.
The order in which you write the list will determine how the hooks will be ran.

For example, if you designed your partition structure to have encryption at the
lowest level, and then you import your zpool, you can say `triggers=luks,zfs`
which would run the encryption hook first, and then ZFS related stuff.

The supported triggers are:

* luks
* zfs

If you don't specify any triggers, than just the default initramfs
commands will be executed.

#### ZFS

`by` - Specifies what directory you want to use when looking for your zpool so
that we can import it.

Supported: by= dev, id, uuid, partuuid, label, partlabel, literal path.

Examples:
* by=label -> /dev/disk/by-label
* by=uuid  -> /dev/disk/by-uuid
* by=dev   -> /dev
* by=/mystical/ninja -> /mystical/ninja

`refresh` - Ignores the zpool.cache in the rootfs, creates a new one
inside the initramfs at import, and then copies it into the rootfs.
* example: linux <kernel> root=tank/gentoo/root refresh

#### LUKS

Follow the same instructions as above, but also add "enc_drives=" and "enc_type"
to your kernel line. If you don't enter them, the initramfs will just ask you
for it.

`enc_drives` - Encrypted drives (You need the enc_type variable below as well)

If you have your zpool on spread over multiple drives, you can pass them all
to this variable as well:
* example: linux \<kernel\> enc_drives=/dev/sda2,/dev/sdb3,/dev/sdc4,/dev/sdd5,/dev/sde6
* example: linux \<kernel\> enc_drives=/dev/sd?2
* example: linux \<kernel\> enc_drives=/dev/disk/by-id/ata-*-part2

`enc_type` - What type of method will you use to decrypt?
Types: pass - passphrase

`key` - plain keyfile

`key_gpg` - keyfile encrypted with gpg

`enc_key_drive` - What drive the keyfile in?
* example: linux \<kernel\> enc_drives=/dev/sda3 enc_type=key enc_key_drive=/dev/sdb1
* example: linux \<kernel\> enc_drives=/dev/sda3 enc_type=key enc_key_drive=UUID=4443433f-5f03-475f-974e-5345fd524c34

`enc_key` - What is the path to the keyfile? You basically pass to grub where in
the drive the file is located (After the initramfs mounts the drive that you
have the key in).
* example: linux <kernel> enc_drives=/dev/sda3 enc_type=key enc_key_drive=/dev/sdb1 enc_key=/keys/root.gpg

In this example, once the initramfs mounts /dev/sdb1, it will look for the
/keys/root.gpg at /dev/sdb1. So if the initramfs mounts /dev/sdb1 at /mnt/key,
it will look for the key at /mnt/key/keys/root.gpg.

`enc_key_ignore` - Ignores the embedded keyfile
* example: linux <kernel> enc_key_ignore

`enc_options` - Allows you to pass options to the 'cryptsetup' command
* example: linux <kernel> enc_drives=/dev/sda3,/dev/sda4 enc_options="--allow-discards"

`enc_tries` - Allows you to set how many times you can retype your passphrase before the initramfs fails to unlock your drives (default is 5)
* example: linux <kernel> enc_tries=10

`enc_targets` - What /dev/mapper/TARGET_NAME to use? Comma separated list, same order as `enc_drives`!  Optional, if not specified names will be generated based on `enc_drives`.
* example: linux \<kernel\> enc_drives=/dev/sda1,/dev/sdb1 enc_targets=crypt_sda,crypt_sdb

LUKS passphrase/key: The easiest way to pass the passphrase is just to wait till
the initramfs asks you for it. When this happens, it will use the _same_
passphrase (or same key) for all your pools. This is to make it convenient for
you. It would be annoying to have a zpool on 6 drives (Encrypted RAIDZ2 let's
say), and then you had to put the password for each one. If you still want to do
this, then just leave the passphrase blank when the initramfs asks you for it.

### Bootloader

See [bootloader.txt](bootloader.txt) for more detailed examples of how to
use the kernel options above.

### Modules

If you require certain kernel modules for boot, you'll need them built into
the initramfs.  Create or update a `config.ini` (see `config-default.ini` for
more details and examples) and include a `[Modules]` section, with one module
name per line.  These modules (and their dependencies) will be included when
building the initramfs.

### Firmware

If you want to include firmware inside your initramfs, create or update a
`config.ini` (see `config-default.ini` for more details and examples) and:

1. Include a `[Firmware]` section which specifies `use = 1`
2. Either:
   * Also specify `copy_all = 1` or
   * (Better:) Include a `[FirmwareFiles]` section, with one file per line.
     these files will be copied from your system's /lib/firmware directory.
     Entries here should be relative to this directory.

### Embedded Keyfile

The initramfs has the ability to embed your encrypted drive(s)'s keyfile
directly into itself.

Some of the benefits this may provide are:
* Not having to type multiple passphrases during boot.
* Rely on an external drive in order to decrypt the drive.
* If using an external drive, reduce the number of files on the /boot drive
  (just kernel and initramfs).

This was primarily implemented in order to reduce the number of passphrases
needed to 1, when you have your /boot directory inside of an encrypted /
partition on LUKS. You will need to have GRUB decrypt your / partition and once
the initramfs loads, it will automatically use the embedded keyfile to decrypt
the drives, and start up your system.

In order to activate this, go into pkg/hooks/Luks.py and change the
"_use_keyfile" value to 1, and then set the "_keyfile_path" to the path on disk
from where to copy your keyfile from. Once this is done, during initramfs
generation, you will see a message that the initramfs is embedding the keyfile
into itself.

In your grub command line, you will need to have the "enc_type" set to "key".

When the initramfs starts up, if it detects that your initramfs has an embedded
keyfile, it will automatically try to decrypt the drives listed in "enc_drives"
and not ask you any questions. If you want to use some other form of decryption
(passphrase, key_gpg), but you don't want to remake the initramfs in order to
remove the keyfile out of it, use the "enc_key_ignore" kernel line option.

### LUKS Detached Header File Support

The initramfs has the ability to embed your detached luks header directly. This
has a lot of security benefits, the main ones being that:

1. Your LUKS device will look as if it was just a bunch of random data
   (plausible deniability).
2. Your LUKS device will pretty much be impossible to decrypt with modern
   technological standards due to the SALT no longer being on the same device as
   the LUKS device.

In order to activate this feature, customize the `[Luks]` section of your
`config.ini` file (create one if necessary).  Refer to `config-default.ini` for
documentation and examples for the relevant settings.

Once this is done, use `enc_options=--header=/etc/header` in the initramfs to
tell the initramfs at boot time where to find the header file.

## License

Released under the Apache License 2.
