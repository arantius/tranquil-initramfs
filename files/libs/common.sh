# Copyright 2012-2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Function to start rescue shell
rescue_shell()
{
	ewarn "Booting into rescue shell..." && eline
	hostname ${HOSTN} && setsid cttyhack /bin/bash -l
}

# Module loading function
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

# Function for parsing command line options
get_opt()
{
	echo "${1#*=}"
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
		enc_drives\=*)
			enc_drives="$(get_opt ${x})"
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
		init\=*)
			INIT="$(get_opt ${x})"
			;;
		refresh)
			refresh="1"
			;;
		recover)
			recover="1"
			;;
		su)
			su="1"
			;;
		redetect)
			redetect="1"
			;;
		esac
	done

	if [[ -z ${root} ]]; then
		die "You must pass the 'root' variable."
	fi
}

# Extract all the drives needed to decrypt before mounting the pool
get_drives()
{
	if [[ -z ${enc_drives} ]]; then
		eqst "Please enter your encrypted drives: " ; read enc_drives
		
		if [[ -z ${enc_drives} ]]; then
			die "No encrypted drives have been entered."
		fi
	fi
	
	drives=($(echo ${enc_drives} | tr "," "\n"))
	
	for i in $(seq 0 $((${#drives[@]} - 1))); do
		eflag "Drive ${i}: ${drives[${i}]}"
	done
}

# Gets a decryption key without displaying it on screen
get_decrypt_key()
{
	unset code

	if [[ $1 == "pass" ]]; then
		while [[ -z ${code} ]]; do
			eqst "Enter passphrase: " ; read -s code ; eline
		done
	elif [[ $1 == "key_gpg" ]]; then
		while [[ -z ${code} ]]; do
			eqst "Enter decryption key: " ; read -s code ; eline
		done
	else
		die "Either a decryption type wasn't passed or it's not supported!"
	fi
}

# Returns the encryption type that will be used interactively from the user
ask_for_enc_type()
{
	local choice=""
	
	einfo "Please enter the encryption type that will be used:"
	eflag "1. Passphrase"
	eflag "2. Unencrypted Key File"
	eflag "3. GPG Encrypted Key File"
	eqst "Current choice [1]: " ; read choice
	
	local good="no"
	while [[ ${good} == "no" ]]; do
		case ${choice} in
		""|1) enc_type="pass" && good="yes" ;;
		2) enc_type="key" && good="yes" ;;
		3) enc_type="key_gpg" && good="yes" ;;
		*) eqst "Invalid input. Please enter a correct choice: " ; read choice
		esac
	done
}

# Detects the available drives
detect_available_drives()
{
	local timer=3
	
	if [[ -z ${redetect} ]]; then
		einfo "Detecting available drives..." && sleep ${timer} && ls /dev/[sv]d*
	else
		local keep_going="yes"
		while [[ ${keep_going} == "yes" ]]; do
			einfo "Detecting available drives..." && sleep ${timer} && ls /dev/[sv]d*

			local choice=""
			eqst "Attempt to re-detect drives? [y/N]: " ; read choice
			timer=0

			if [[ ${choice} != "y" ]] && [[ ${choice} != "Y" ]]; then
				keep_going="no"
			fi
		done
	fi
}

# Run this function if USE_LUKS is enabled
luks_trigger()
{
	einfo "Gathering encrypted devices..." && get_drives

	# If the user left their enc_type blank (Could be intentional),
	# then let's ask them now to select the type.
	if [[ -z ${enc_type} ]]; then
		ask_for_enc_type

		if [[ -z ${enc_type} ]]; then
			die "The encryption type was not set."
		fi
	fi

	if [[ ${enc_type} != "pass" ]] && [[ ${enc_type} != "key" ]] && [[ ${enc_type} != "key_gpg" ]]; then
		die "Invalid 'enc_type' option. Only 'pass', 'key', and 'key_gpg' are supported."
	fi

	# Gathers information required (passphrase, keyfile location, etc)
	if [[ ${enc_type} == "pass" ]]; then
		get_decrypt_key "pass"
	elif [[ ${enc_type} == "key" ]] || [[ ${enc_type} == "key_gpg" ]]; then
		detect_available_drives

		# What drive is the keyfile in?
		if [[ -z ${enc_key_drive} ]]; then
			eqst "Enter drive where keyfile is located: " ; read enc_key_drive

			if [[ -z ${enc_key_drive} ]]; then
				die "Error setting path to keyfile's drive!"
			fi
		fi

		# What is the path to the keyfile?
		if [[ -z ${enc_key} ]]; then
			eqst "Enter path to keyfile: " ; read enc_key

			if [[ -z ${enc_key} ]]; then
				die "Error setting path to keyfile!"
			fi
		fi

		# What is the decryption key for the keyfile?
		if [[ ${enc_type} == "key_gpg" ]]; then
			get_decrypt_key "key_gpg"
		fi

		# Mount the drive
		mount ${enc_key_drive} ${KEY_DRIVE}

		# Set path to keyfile
		keyfile="${KEY_DRIVE}/${enc_key}"
	fi

	# Attempt to decrypt the drives
	decrypt_drives
	
	# Unmount the drive with the keyfile if we had one
	if [[ ${enc_type} == "key" ]] || [[ ${enc_type} == "key_gpg" ]]; then
		umount ${enc_key_drive}
		
		if [[ $? -eq 0 ]]; then
			einfo "Your key drive has been unmounted successfully."
		else
			ewarn "Error unmounting your key drive."
		fi
	fi
}

# Attempts to decrypt the drives
decrypt_drives()
{
	if [[ -z ${drives} ]]; then
		die "Failed to get encrypted drives. The 'drives' value is empty."
	fi

	# Set up a counter in case the user gave an incorrect passphrase/key_gpg decryption code
	local count=0
	local max=3

	for i in $(seq 0 $((${#drives[@]} - 1))); do
		if [[ ${enc_type} == "pass" ]]; then
			while [[ ${count} -lt ${max} ]]; do
				echo "${code}" | cryptsetup luksOpen ${drives[${i}]} vault_${i} && break 
				
				if [[ $? -ne 0 ]]; then
					count=$((count + 1))
					
					# If the user kept failing and reached their max tries,
					# then throw them into a rescue shell
					if [[ ${count} -eq ${max} ]]; then
						die "Failed to decrypt: ${drives[${i}]}"
					else
						get_decrypt_key "pass"
					fi
				fi		
			done
		elif [[ ${enc_type} == "key" ]]; then
			if [[ ! -e ${keyfile} ]]; then
				die "The keyfile doesn't exist in this path: ${keyfile}"
			fi

			cryptsetup --key-file "${keyfile}" luksOpen ${drives[${i}]} vault_${i} || \
			die "Failed to decrypt: ${drives[${i}]}"
			
		elif [[ ${enc_type} == "key_gpg" ]]; then
			if [[ ! -e ${keyfile} ]]; then
				die "The keyfile doesn't exist in this path: ${keyfile}"
			fi

			while [[ ${count} -lt ${max} ]]; do
				echo "${code}" | gpg --batch --passphrase-fd 0 -q -d ${keyfile} 2> /dev/null | \
				cryptsetup --key-file=- luksOpen ${drives[${i}]} vault_${i} && break
				
				if [[ $? -ne 0 ]]; then
					count=$((count + 1))
					
					# If the user kept failing and reached their max tries,
					# then throw them into a rescue shell
					if [[ ${count} -eq ${max} ]]; then
						die "Failed to decrypt: ${drives[${i}]}"
					else
						get_decrypt_key "key_gpg"
					fi
				fi
			done
		fi
	done
}

# Run this function if USE_ZFS is enabled
zfs_trigger()
{
	POOL_NAME="${root%%/*}"

	eflag "Importing ${POOL_NAME}..."

	CACHE="/etc/zfs/zpool.cache"

	if [[ ! -f "${CACHE}" ]]; then
		ewarn "No cache file exists, importing your pool without it ..."
		zpool import -f -N -o cachefile= ${POOL_NAME}
	elif [[ -f "${CACHE}" ]] && [[ "${refresh}" == "1" ]]; then
		ewarn "Ignoring cache file and importing your pool ..."
		ewarn "Please recreate your initramfs so that it can use your new zpool.cache!"

		sleep 3

		zpool export -f ${POOL_NAME} 2> /dev/null
		zpool import -f -N -o cachefile= ${POOL_NAME}
	fi
}

# Mounts your root device
mount_root()
{
	einfo "Mounting your root device..."

	# Using "" for the ${options} below so that if the user doesn't have any
	# options, the variable ends up expanding back to empty quotes and allows
	# the mount command to keep going.
	if [[ ${USE_ZFS} == "1" ]]; then
		# Try to mount the pool now, if it fails then there might have been
		# a problem with the cache, so try to remount the pool and then try
		# again before failing.
		mount -t zfs -o zfsutil,"${options}" ${root} ${NEW_ROOT} || \
		die "Failed to import your zfs root dataset!"

		# Installs the cache generated by this initramfs run to the rootfs.
		# This prevents the main system from becoming out of sync with what
		# the initramfs is working with.
		install_cache
	else
		mount -o "${options}" ${root} ${NEW_ROOT} || \
		die "Failed to import your root device!"
	fi
}

# Switches into your root device
switch_to_root()
{
	einfo "Switching into your root device..." && eline
	exec switch_root ${NEW_ROOT} ${INIT}
}

# Checks all triggers
check_triggers()
{
	if [[ ${USE_LUKS} == "1" ]]; then
		luks_trigger
	fi

	if [[ ${USE_ZFS} == "1" ]]; then
		zfs_trigger
	fi
}

# Installs the zpool.cache to the rootfs
install_cache()
{
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

	setsid cttyhack /bin/bash -c "chroot ${NEW_ROOT} /bin/bash -c 'hostname ${RHOSTN}' && chroot ${NEW_ROOT} /bin/bash -l"

	# Lazy unmount these devices from the rootfs since they will be fully
	# unmounted from the initramfs environment right after this function
	# is over.
	umount -l ${NEW_ROOT}/proc ${NEW_ROOT}/dev ${NEW_ROOT}/sys
}

### Utility Functions ###

# Used for displaying information
einfo()
{
	echo -e "\e[1;32m[*]\e[0;m ${@}"
}

# Used for input (questions)
eqst()
{
	echo -en "\e[1;37m[*]\e[0;m ${@}"
}

# Used for warnings
ewarn()
{
	echo -e "\e[1;33m[!]\e[0;m ${@}"
}

# Used for flags
eflag()
{
	echo -e "\e[1;34m[+]\e[0;m ${@}"
}

# Used for errors
die()
{
	echo -e "\e[1;31m[#]\e[0;m ${@}" && rescue_shell
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
