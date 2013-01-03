#!/bin/busybox sh

# Copyright (C) 2012 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Welcome Message
welcome()
{
        einfo "Welcome to the Bliss Initramfs!"
}

# Function to start rescue shell
rescue_shell()
{
	ewarn "Booting into rescue shell..."
	busybox --install -s
	exec /bin/sh
}

# Function to load ZFS modules
load_modules()
{
        modules=""

        if [ "${USE_ZFS}" = "1" ]; then
                modules="${modules} spl splat zavl znvpair zcommon zunicode zfs zpios"
        fi

        for x in ${modules}; do
                # If it's the ZFS module, and there is a cachesize set, then set the arc max to it
                if [ "${x}" = "zfs" ] && [ ! -z "${cache_size}" ]; then
                        modprobe ${x} zfs_arc_max=${cache_size}
                else
                        modprobe ${x}
                fi
        done
}

# Prevent kernel from printing on screen
prevent_printk()
{
        echo 0 > /proc/sys/kernel/printk
}

# Mount Kernel Devices
mnt_kernel_devs()
{
        mount -t proc none /proc
        mount -t devtmpfs none /dev
        mount -t sysfs none /sys
}

# Unmount Kernel Devices
umnt_kernel_devs()
{
        umount /proc
        umount /dev
        umount /sys
}

# Handles LUKS stuff, run this function
luks_trigger()
{
        if [ "${USE_LUKS}" = "1" ]; then
                if [ ! -z "${enc_root}" ]; then
                        einfo "Opening up your encrypted drive..."

                        cryptsetup luksOpen ${enc_root} dmcrypt_root || die "luksOpen failed to open: ${enc_root}"
                else
                        die "You didn't pass the 'enc_root' variable to the kernel"
                fi
        fi
}

# Handles ZFS stuff, run this function
zfs_trigger()
{
        if [ "${USE_ZFS}" = "1" ]; then
                einfo "Mounting your zpool..."

                zpool import -f -d /dev -o cachefile= -R ${NEW_ROOT} ${pool_name} || die "Failed to import your zpool"
        fi
}

switch_to_new_root()
{
        exec switch_root ${NEW_ROOT} ${NEW_INIT} || die "Failed to switch to your rootfs"
}

# Utility Functions

# Used for displaying information
einfo() 
{
        eline && echo -e "\033[1;32m>>>\033[0;m ${@}"
}

# Used for warnings
ewarn() 
{
        eline && echo -e "\033[1;33m>>>\033[0;m ${@}"
}

# Used for flags
eflag() 
{
        eline && echo -e "\033[1;35m>>>\033[0;m ${@}"
}

# Used for options
eopt() 
{
        echo -e "\033[1;36m>>\033[0;m ${@}"
}

# Used for errors
die() 
{
        eline && echo -e "\033[1;31m>>> ${@} <<<\033[0;m" || rescue_shell 
}

# Prints empty line
eline()
{
        echo ""
}
