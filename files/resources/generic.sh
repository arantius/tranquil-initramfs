# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Function to start rescue shell
rescue_shell()
{
	ewarn "Booting into rescue shell..." && eline
	exec setsid /bin/bash -c 'exec /bin/bash </dev/tty1 >/dev/tty1 2>&1'
}

# Function to load ZFS modules
load_modules()
{
        if [ "${USE_ZFS}" == "1" ]; then
		modules=""

		for x in ${modules}; do
			# If it's the ZFS module, and there is a arcmax set, then set the arc max to it
			if [ "${x}" == "zfs" -a ! -z "${arcmax}" ]; then
				modprobe ${x} zfs_arc_max="${arcmax}"
			else
				modprobe ${x}
			fi
		done
        fi
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

# Function for parsing command line options with "=" in them
get_opt() {
	echo "${@}" | cut -d "=" -f 2
}

# Process command line options
parse_cmdline()
{
	for x in $(cat /proc/cmdline); do
		case ${x} in
		root\=*)
			root=$(get_opt ${x})
			;;
		init\=*)
			INIT=$(get_opt ${x})
			;;
		enc_root\=*)
			enc_root=$(get_opt ${x})
			;;
                enc_type\=*)
                        enc_type=$(get_opt ${x})
                        ;;
		nocache)
			nocache="1"
			;;
		recover)
			recover="1" 
			;;
		refresh)
			refresh="1"
			;;
		su)
			su="1"
			;;
		esac
	done
}

# Extract all the drives needed to decrypt before mounting the pool
get_drives()
{
        drives=($(echo ${enc_root} | tr "," "\n"))
}

# If USE_LUKS is enabled, run this function
luks_trigger()
{
        if [ -z "${enc_root}" ]; then
                die "You didn't pass the 'enc_root' variable to the kernel. Example: enc_root=/dev/sda2,/dev/sdb2"
        fi

        einfo "Gathering encrypted devices..." && get_drives

	for i in $(seq 0 $((${#drives[@]} - 1))); do
		eflag "Drive ${i}: ${drives[${i}]}"
	done

        if [ -z "${enc_type}" ]; then
                die "You didn't pass the 'enc_type' variable to the kernel. Example enc_type=[pass,key,key-gpg]"
	elif [ "${enc_type}" != "pass" -a "${enc_type}" != "key" -a "${enc_type}" != "key_gpg" ]; then
		die "You have passed an invalid option. Only "pass", "key", and "key_gpg" are supported."
        else
		# Gathers information required (passphrase, keyfile location, etc)
                if [ "${enc_type}" == "pass" ]; then
                        eqst "Enter passphrase (Leave blank if more than 1): " && read -s code && eline
                elif [ "${enc_type}" == "key" -o "${enc_type}" == "key_gpg" ]; then
                        einfo "Detecting available drives..." && sleep 3 && ls /dev/sd*

			eqst "Enter drive where keyfile is located: " && read drive

			mount ${drive} ${KEY_DRIVE}

			eqst "Enter relative path to keyfile: " && read file

			local key_path="${KEY_DRIVE}/${file}"

			eqst "Enter decryption phrase: " && read -s phrase && eline

			if [ -z "${phrase}" ]; then
				die "No decryption phrase was given."
			fi
		fi

		if [ ! -z "${drives}" ]; then
			einfo "Opening up your encrypted drive(s)..."

			for i in $(seq 0 $((${#drives[@]} - 1))); do
				if [ "${enc_type}" == "pass" ]; then
					if [ ! -z "${code}" ]; then
						echo "${code}" | cryptsetup luksOpen ${drives[${i}]} vault_${i} || die "luksOpen failed to open: ${drives[${i}]}"
					else
						cryptsetup luksOpen ${drives[${i}]} vault_${i} || die "luksOpen failed to open: ${drives[${i}]}"
					fi        
				elif [ "${enc_type}" == "key" ]; then
					if [ -f "${key_path}" ]; then
						cryptsetup --key-file "${key_path}" luksOpen ${drives[${i}]} vault_${i} || die "luksOpen failed to open: ${drives[${i}]}"
					else
						die "Keyfile doesn't exist in this path: ${key_path}"
					fi
				elif [ "${enc_type}" == "key_gpg" ]; then
					if [ -f "${key_path}" ]; then
						echo "${phrase}" | gpg --batch --passphrase-fd 0 -q -d ${key_path} 2> /dev/null | 
						cryptsetup --key-file=- luksOpen ${drives[${i}]} vault_${i} || die "luksOpen failed to open: ${drives[${i}]}"
					else
						die "Keyfile doesn't exist in this path: ${file}"
					fi
				fi
			done

			# Umount the drive with the keyfile if we had one
			umount ${drive} > /dev/null 2>&1
		else
			die "Failed to get drives.. The 'drives' value is empty"
		fi
        fi
}

# If USE_ZFS is enabled, run this function
zfs_trigger()
{
        if [ -z "${root}" ]; then
		die "You must pass the root= variable. Example: root=rpool/ROOT/funtoo"
	fi

        pool_name="${root%%/*}"

        eflag "Mounting ${pool_name}..."

	local CACHE="/etc/zfs/zpool.cache"

	if [ ! -f "${CACHE}" -o "${nocache}" = "1" -o "${refresh}" = "1" ]; then
                remount_pool
	fi

        mount -t zfs -o zfsutil ${root} ${NEW_ROOT} || die "Failed to import your zfs root dataset"
}

# Self explanatory
switch_to_new_root()
{
        exec switch_root ${NEW_ROOT} ${INIT} || die "Failed to switch to your rootfs"
}

# Checks all triggers
check_triggers()
{
        if [ "${USE_LUKS}" == "1" ]; then
                luks_trigger
        fi

        if [ "${USE_ZFS}" == "1" ]; then
                zfs_trigger
        fi
}

# Regenerates a brand new zpool.cache file and installs it in the system
refresh_cache()
{
        eflag "Refreshing zpool.cache..."
	
        local CACHE="/etc/zfs/zpool.cache"

        check_triggers

        # If there is an old cache in the rootfs, then delete it.
        if [ -f "${NEW_ROOT}/${CACHE}" ]; then
                rm -f ${NEW_ROOT}/${CACHE}
        fi

        cp -f ${CACHE} ${NEW_ROOT}/${CACHE}

        ewarn "Please recreate your initramfs so that it can use the new zpool.cache!"
        sleep 3

        # Now that we refreshed the cache, let's just continue into the OS
	have_a_nice_day
}

# Single User Mode
single_user()
{
        check_triggers
        chroot ${NEW_ROOT} /bin/bash --login
}

# Cleanly exports and imports pool

# I made this function since Gentoo/Funtoo doesn't cleanly umount the pool
# during shutdown/restart. This is actually only used if we aren't going to
# be using the zpool.cache.
remount_pool()
{
       	zpool export -f ${pool_name} > /dev/null 2>&1
        zpool import -f -N -o cachefile= ${pool_name} || die "Failed to import your pool: ${pool_name}"
}

# Central exit point needed to cleanly exit from either the main function
# or the refresh_cache function.
have_a_nice_day()
{
	einfo "Unmounting kernel devices..."
	umnt_kernel_devs || die "Failed to umount kernel devices"

	einfo "Switching to your rootfs..." && eline
	switch_to_new_root
}

### Utility Functions ###

# Used for displaying information
einfo()
{
        eline && echo -e "\e[1;32m>>>\e[0;m ${@}"
}

# Used for input (questions)
eqst()
{
        eline && echo -en "\e[1;37m>>>\e[0;m ${@}"
}

# Used for warnings
ewarn()
{
        eline && echo -e "\e[1;33m>>>\e[0;m ${@}"
}

# Used for flags
eflag()
{
        eline && echo -e "\e[1;34m>>>\e[0;m ${@}"
}

# Used for errors
die()
{
        eline && echo -e "\e[1;31m>>>\e[0;m ${@}" && rescue_shell 
}

# Prints empty line
eline()
{
        echo ""
}

# Welcome Message
welcome()
{
        einfo "Welcome to Bliss! [${VERSION}]"
}

# Prevent kernel from printing on screen
prevent_printk()
{
        echo 0 > /proc/sys/kernel/printk
}
