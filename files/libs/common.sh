# Copyright (C) 2012-2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Function to start rescue shell
rescue_shell()
{
	ewarn "Booting into rescue shell..." && eline
	hostname ${HOSTN} && setsid cttyhack /bin/bash
}

# Function to load ZFS modules
load_modules()
{
        if [[ ${USE_ZFS} == "1" ]] || [[ ${USE_ADDON} == "1" ]]; then
		einfo "Loading modules..."

		modules=""

		for x in ${modules}; do
			modprobe ${x}
		done
        fi
}

# Mount Kernel Devices
mnt_kernel_devs()
{
	einfo "Mounting kernel devices..."

        mount -t proc none /proc
        mount -t devtmpfs none /dev
        mount -t sysfs none /sys
}

# Unmount Kernel Devices
umnt_kernel_devs()
{
	einfo "Unmounting kernel devices..."

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
	einfo "Parsing command line values..."

	for x in $(cat /proc/cmdline); do
		case ${x} in
		root\=*)
			root="$(get_opt ${x})"
			;;
		enc_root\=*)
			enc_root="$(get_opt ${x})"
			;;
                enc_type\=*)
                        enc_type="$(get_opt ${x})"
                        ;;
                enc_key\=*)
                        enc_key="$(get_opt ${x})"
                        ;;
                enc_key_drive\=*)
                        enc_key_drive="$(get_opt ${x})"
                        ;;
		options\=*)
			options="$(get_opt ${x})"
			;;
		recover)
			recover="1"
			;;
		su)
			su="1"
			;;
		esac
	done

	if [[ -z ${root} ]]; then
		die "You must pass the root= variable. Example: root=rpool/ROOT/funtoo, /dev/sda3"
	fi
}

# Extract all the drives needed to decrypt before mounting the pool
get_drives()
{
        drives=($(echo ${enc_root} | tr "," "\n"))
}

# If USE_LUKS is enabled, run this function
luks_trigger()
{
        if [[ -z ${enc_root} ]]; then
                die "You didn't pass the 'enc_root' variable to the kernel. Example: enc_root=/dev/sda2,/dev/sdb2"
        fi

        einfo "Gathering encrypted devices..." && get_drives

	for i in $(seq 0 $((${#drives[@]} - 1))); do
		eflag "Drive ${i}: ${drives[${i}]}"
	done

        if [[ -z ${enc_type} ]]; then
                die "You didn't pass the 'enc_type' variable to the kernel. Example enc_type=[pass,key,key-gpg]"
	elif [[ ${enc_type} != "pass" ]] && [[ ${enc_type} != "key" ]] && [[ ${enc_type} != "key_gpg" ]]; then
		die "You have passed an invalid option. Only "pass", "key", and "key_gpg" are supported."
        else
		# Gathers information required (passphrase, keyfile location, etc)
                if [[ ${enc_type} == "pass" ]]; then
                        eqst "Enter passphrase (Leave blank if more than 1): " && read -s code && eline
                elif [[ ${enc_type} == "key" ]] || [[ ${enc_type} == "key_gpg" ]]; then
                        einfo "Detecting available drives..." && sleep 3 && ls /dev/sd*

			# What drive is the keyfile in?
			if [[ -z ${enc_key_drive} ]]; then
				eqst "Enter drive where keyfile is located: " && read enc_key_drive && eline

				if [[ -z ${enc_key_drive} ]]; then
					die "Error setting path to keyfile's drive!"
				fi
			fi

			# What is the path to the keyfile?
			if [[ -z ${enc_key} ]]; then
				eqst "Enter path to keyfile: " && read enc_key && eline

				if [[ -z ${enc_key} ]]; then
					die "Error setting path to keyfile!"
				fi
			fi

			# What is the decryption key?
			if [[ ${enc_type} == "key_gpg" ]]; then
				eqst "Enter decryption code: " && read -s code && eline

				if [[ -z ${code} ]]; then
					die "No decryption code was given."
				fi
			fi

			# Mount the drive
			mount ${enc_key_drive} ${KEY_DRIVE}

			# Set path to keyfile
			keyfile="${KEY_DRIVE}/${enc_key}"
		fi

		if [[ ! -z ${drives} ]]; then
			einfo "Opening up your encrypted drive(s)..."

			for i in $(seq 0 $((${#drives[@]} - 1))); do
				if [[ ${enc_type} == "pass" ]]; then
					if [[ ! -z ${code} ]]; then
						echo "${code}" | cryptsetup luksOpen ${drives[${i}]} vault_${i} || die "luksOpen failed to open: ${drives[${i}]}"
					else
						cryptsetup luksOpen ${drives[${i}]} vault_${i} || die "luksOpen failed to open: ${drives[${i}]}"
					fi
				elif [[ ${enc_type} == "key" ]]; then
					if [[ -f ${keyfile} ]]; then
						cryptsetup --key-file "${keyfile}" luksOpen ${drives[${i}]} vault_${i} || die "luksOpen failed to open: ${drives[${i}]}"
					else
						die "Keyfile doesn't exist in this path: ${keyfile}"
					fi
				elif [[ ${enc_type} == "key_gpg" ]]; then
					if [[ -f ${keyfile} ]]; then
						echo "${code}" | gpg --batch --passphrase-fd 0 -q -d ${keyfile} 2> /dev/null |
						cryptsetup --key-file=- luksOpen ${drives[${i}]} vault_${i} || die "luksOpen failed to open: ${drives[${i}]}"
					else
						die "Keyfile doesn't exist in this path: ${keyfile}"
					fi
				fi
			done

			# Umount the drive with the keyfile if we had one
			umount ${enc_key_drive} > /dev/null 2>&1
		else
			die "Failed to get drives.. The 'drives' value is empty"
		fi
        fi
}

# If USE_RAID is enabled, run this function
raid_trigger()
{
	# Scan for raid arrays and save them in mdadm.conf
	mdadm --examine --scan > /etc/mdadm.conf || rescue_shell

	# Assemble all raid devices
	mdadm --assemble --scan 2> /dev/null || rescue_shell
}

# If USE_LVM is enabled, run this function
lvm_trigger()
{
	# Make LVM Volume Group/Pools available 
	lvm vgchange -a y || rescue_shell
	lvm vgscan --mknodes || rescue_shell
}

# If USE_ZFS is enabled, run this function
zfs_trigger()
{
        pool_name="${root%%/*}"

        eflag "Importing ${pool_name}..."
        zpool import -f -N -o cachefile= ${pool_name} || die "Failed to import your pool: ${pool_name}"
}

# Mounts your root device
mount_root()
{
	einfo "Mounting your root device..."

	# Using "" for the ${options} below so that if the user doesn't have any options,
	# the variable ends up expanding back to empty quotes and allows the mount command
	# to keep going. 
	if [[ ${USE_ZFS} == "1" ]]; then
        	mount -t zfs -o zfsutil,"${options}" ${root} ${NEW_ROOT} || die "Failed to import your zfs root dataset!"

		# Installs the cache generated by this initramfs run to the rootfs. This prevents the main system from
		# becoming out of sync with what the initramfs is working with.
		install_cache
	else
		mount -o "${options}" ${root} ${NEW_ROOT} || die "Failed to import your root device!"
	fi

}

# Switches into your root device
switch_to_root()
{
	einfo "Switching into your root device..." && eline

        exec switch_root ${NEW_ROOT} ${INIT} 2> /dev/null || die "Failed to switch into your root device!"
}

# Checks all triggers
check_triggers()
{
        if [[ ${USE_LUKS} == "1" ]]; then
                luks_trigger
        fi

        if [[ ${USE_RAID} == "1" ]]; then
                raid_trigger
        fi

        if [[ ${USE_LVM} == "1" ]]; then
                lvm_trigger
        fi

        if [[ ${USE_ZFS} == "1" ]]; then
                zfs_trigger
        fi
}

# Installs the zpool.cache generated by the initramfs to the rootfs
install_cache()
{
        local CACHE="/etc/zfs/zpool.cache"

        # If there is an old cache in the rootfs, then delete it.
        if [[ -f ${NEW_ROOT}/${CACHE} ]]; then
                rm -f ${NEW_ROOT}/${CACHE}
        fi

        cp -f ${CACHE} ${NEW_ROOT}/${CACHE}
}

# Single User Mode
single_user()
{
	ewarn "Booting into single user mode..." && eline

	mount --rbind /proc ${NEW_ROOT}/proc
	mount --rbind /dev ${NEW_ROOT}/dev
	mount --rbind /sys ${NEW_ROOT}/sys

	setsid cttyhack /bin/bash -c "chroot ${NEW_ROOT} /bin/bash -c \
	'cat /proc/mounts > /etc/mtab && hostname ${RHOSTN}' && \
	chroot ${NEW_ROOT} /bin/bash -l"

	# Lazy unmount these devices from the rootfs since they will be fully 
	# unmounted from the initramfs environment right after this function is over.
	umount -l ${NEW_ROOT}/proc ${NEW_ROOT}/dev ${NEW_ROOT}/sys 
}

### Utility Functions ###

# Used for displaying information
einfo()
{
        echo -e "\e[1;32m*\e[0;m ${@}"
}

# Used for input (questions)
eqst()
{
        echo -en "\e[1;37m*\e[0;m ${@}"
}

# Used for warnings
ewarn()
{
        echo -e "\e[1;33m*\e[0;m ${@}"
}

# Used for flags
eflag()
{
        echo -e "\e[1;34m*\e[0;m ${@}"
}

# Used for errors
die()
{
        echo -e "\e[1;31m*\e[0;m ${@}" && rescue_shell
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
