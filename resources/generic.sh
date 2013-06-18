# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Message that will be displayed at the top of the screen
print_header()
{
	echo -e "-----------------------------------"
	echo -e "\e[1;33m| ${NAME} - v${VERSION}\e[0;m"
	echo -e "\e[1;33m| Author: ${CONTACT}\e[0;m"
	echo -e "\e[1;33m| Distributed under the ${LICENSE}\e[0;m"
	echo -e "-----------------------------------"
}

# Display the menu
print_menu()
{
	# Check to see if a menu option was passed
	if [ -z "${CHOICE}" ]; then
		einfo "Which initramfs would you like to generate:"
		eline
		print_options
		eqst "Current choice [1]: " && read CHOICE
	fi

	case ${CHOICE} in
	1|"")
		einfo "An initramfs for ZFS will be generated!"
		. hooks/base.sh
		. hooks/zfs.sh
		. hooks/addon.sh
		;;
        2)
                einfo "An initramfs for LUKS + ZFS will be generated!"
		. hooks/base.sh
		. hooks/zfs.sh
                . hooks/luks.sh
		. hooks/addon.sh
                ;;
	3)
		unset CHOICE
		print_more
		;;
	*)
		ewarn "Exiting." && exit
		;;
	esac
}

# This prints out the "More Options" choice
print_more()
{
	einfo "More Options:"
	eline
	eopt "1. SLAX Bundle (ZFS)"
	eopt "2. Back"
	eopt "3. Exit Program"
	eqst "Current choice [1]: " && read CHOICE

	case ${CHOICE} in
	1|"")
		einfo "Creating a SLAX Bundle for ZFS!"
		. hooks/srm/zfs_srm.sh
		. hooks/zfs.sh
		;;
	2)
		unset CHOICE && clear
		print_header
		print_menu
		;;
	*)
		ewarn "Exiting." && exit
		;;
	esac
}

# Makes sure that arch is x86_64
get_arch()
{
	case ${ARCH} in
	x86_64)
		LIB_PATH="64"
		einfo "Detected ${LIB_PATH} bit platform"
		;;
	*)
		die "Your architecture isn't supported, exiting"
		;;
	esac
}

# Prints the available options if the user passes an invalid number
print_options()
{
	eopt "1. ZFS"
	eopt "2. Encrypted ZFS (LUKS + ZFS)"
	eopt "3. More Options"
	eopt "4. Exit Program"
}

# Ask the user if they want to use their current kernel, or another one
do_kernel()
{
	if [ "${USE_MODULES}" = "1" ]; then
		# Check to see if a kernel was passed
		if [ -z "${KERNEL}" ]; then
			eqst "Do you want to use the current kernel: $(uname -r)? [Y/n]: " && read CHOICE

			case ${CHOICE} in
			y|Y|"")
				KERNEL=$(uname -r)
				;;
			n|N)
				eqst "Please enter the kernel name: " && read KERNEL
				;;
			*)
				die "Invalid option, re-open the application"
				;;
			esac
		fi
	fi

	# Set modules path to correct location and sets kernel name for initramfs
	if [ "${ZFS_SRM}" = "1" ]; then
		MODULES="/lib/modules/${KERNEL}/"
		LOCAL_MODULES="${TMP_KMOD}/lib/modules/${KERNEL}/"
		SRM_CORE="zfs-core-${KERNEL}.sb"
		SRM_KMOD="zfs-kmod-${KERNEL}.sb"
	elif [ "${USE_MODULES}" = "1" ]; then
		MODULES="/lib/modules/${KERNEL}/"
		LOCAL_MODULES="${TMP_CORE}/lib/modules/${KERNEL}/"
		INITRD="initrd-${KERNEL}.img"
	fi
}


# Message for displaying the generating event
print_start()
{
	if [ "${ZFS_SRM}" = "1" ]; then
		einfo "Creating SBs for ${KERNEL}..."
	else
		einfo "Creating initramfs for ${KERNEL}..."
	fi
}


# Check to see if "${TMP_CORE}" exists, if it does, delete it for a fresh start
# Utility function to return back to home dir and clean up. For exiting on errors
clean()
{
	# Go back to the original working directory so that we are
	# completely sure that there will be no inteference cleaning up.
	cd ${HOME}

	if [ -d ${TMP_CORE} ]; then
		rm -rf ${TMP_CORE}

		if [ -d ${TMP_CORE} ]; then
			echo "Failed to delete the ${TMP_CORE} directory. Exiting..." && exit
		fi

	fi

	if [ -d ${TMP_KMOD} ]; then
		rm -rf ${TMP_KMOD}

		if [ -d ${TMP_KMOD} ]; then
			echo "Failed to delete the ${TMP_KMOD} directory. Exiting..." && exit
		fi
	fi
}


# Check to make sure kernel modules directory exists
check_mods_dir()
{
	if [ "${USE_MODULES}" = "1" ]; then
		einfo "Checking to see if modules directory exists for ${KERNEL}..."

		if [ ! -d "${MODULES}" ]; then
			die "Kernel modules directory doesn't exist for ${KERNEL}. Exiting..."
		fi
	fi
}

# Create the base directory structure for the initramfs
create_dirs()
{
	einfo "Creating directory structure for initramfs..."

	# Make base directories
	mkdir ${TMP_CORE} && mkdir ${TMP_KMOD} && mkdir -p ${CDIRS}

	# Make kernel modules directory
	if [ ! -z ${LOCAL_MODULES} -a "${USE_MODULES}" == "1" ]; then
		mkdir -p ${LOCAL_MODULES}
	fi

	# Make ZFS specific directories
	if [ "${USE_ZFS}" == "1" ]; then
		mkdir -p ${TMP_CORE}/etc/zfs
	fi

	# Make LUKS specific directories
	if [ "${USE_LUKS}" == "1" ]; then
		mkdir -p ${TMP_CORE}/mnt/key
	fi

	# Delete any directories not needed
	strip
}

# Create the required symlinks to it
create_links()
{
	if [ "${USE_BASE}" = "1" ]; then
		einfo "Creating symlinks..."
	
		# Needs to be from this directory so that the links are relative
		cd ${LOCAL_BIN}

		# Create 'sh' symlink to 'bash'
		if [ -L "sh" ]; then
			rm sh
		fi

		ln -s bash sh

		if [ ! -L "sh" ]; then
			die "Error creating link from sh to bash"
		fi

		# Create busybox links
		./busybox --install  .

		cd ${LOCAL_SBIN}
		
		for i in ${KMOD_SYM}; do
			ln -s kmod ${i}
			
			# Remove the busybox equivalent
			rm ${LOCAL_BIN}/${i}
		done
	fi
}

# This function copies and sets up any files needed. mtab, init, zpool.cache
config_files()
{
	einfo "Configuring files..."

	touch ${TMP_CORE}/etc/mtab

	if [ ! -f "${TMP_CORE}/etc/mtab" ]; then
		die "Error created mtab file... Exiting"
	fi

	if [ "${ZFS_SRM}" != "1" ]; then
		# Copy init functions
		cp -r ${HOME}/files/resources/* ${TMP_CORE}/resources/
		
		# Copy the init script
		cp ${HOME}/files/init ${TMP_CORE} 

		# Give execute permission to the script
		chmod u+x ${TMP_CORE}/init

		if [ ! -f "${TMP_CORE}/init" ]; then
			die "Error creating init file... Exiting"
		fi
	fi
	
	# Any last substitions or additions/modifications should be done here
	if [ "${USE_ZFS}" == "1" -a "${ZFS_SRM}" != "1" ]; then
		# Enable ZFS in the init if ZFS is being used.
		sed -i -e "13s/0/1/" ${TMP_CORE}/init

		# Sets initramfs script version number
		sed -i -e "16s/0/${VERSION}/" ${TMP_CORE}/init

		# Copies zpool.cache if it exists
		if [ -f "${ZCACHE}" ]; then
			eqst "Do you want to use the current zpool.cache? [y/N]: " && read CHOICE

			case ${CHOICE} in
			y|Y)
				ewarn "Creating initramfs with zpool.cache"
				cp ${ZCACHE} ${TMP_CORE}/etc/zfs
				;;
			n|N|*)
				ewarn "Creating initramfs without zpool.cache"
				;;
			esac
		else
			ewarn "Creating initramfs without zpool.cache"
		fi
	fi

	# Enable LUKS in the init if LUKS is being used.
	if [ "${USE_LUKS}" == "1" ]; then
		sed -i -e "14s/0/1/" ${TMP_CORE}/init
	fi

	# Plug in the modules that the user wants to load
	if [ "${USE_ADDON}" == "1" ]; then
		sed -i -e "18s/\"\"/\"${ADDON_MODS}\"/" ${TMP_CORE}/resources/generic.sh
	fi
}

# Compresses the kernel modules and generates modprobe table
do_modules()
{
	if [ "${USE_MODULES}" = "1" ]; then
		einfo "Compressing kernel modules..."

		for module in $(find ${LOCAL_MODULES} -name "*.ko"); do
			gzip ${module}
		done
		
		if [ "${ZFS_SRM}" != "1" ]; then
			einfo "Generating modprobe information..."
			
                        # Copy modules.order and modules.builtin just so depmod
                        # doesn't spit out warnings. -_-
                        cp -a ${MODULES}/modules.{order,builtin} ${LOCAL_MODULES}

			depmod -b ${TMP_CORE} ${KERNEL} || die "You don't have depmod? Something is seriously wrong!"
		elif [ "${ZFS_SRM}" = "1" ]; then
			if [ -f "${DEPMOD}/modules.dep" ]; then
				einfo "Copying modprobe information..."
				cp -a ${DEPMOD}/modules.* ${LOCAL_MODULES}
			fi
		fi
	fi
}

# Create the solution
create()
{
	if [ "${ZFS_SRM}" = "1" ]; then
		einfo "Creating and Packing SBs..."

		# Create the Core SB file
		mksquashfs ${TMP_CORE} ${HOME}/${SRM_CORE} -all-root -comp xz -noappend -no-progress | logger

		if [ ! -f "${HOME}/${SRM_CORE}" ]; then
			die "Error creating the Core SRM file.. exiting"
		fi

		# Create the KMod SB file
		mksquashfs ${TMP_KMOD} ${HOME}/${SRM_KMOD} -all-root -comp xz -noappend -no-progress | logger

		if [ ! -f "${HOME}/${SRM_KMOD}" ]; then
			die "Error creating the KMod SRM file.. exiting"
		fi
	else
		einfo "Creating and Packing initramfs..."

		# The find command must use the `find .` and not `find ${TMP_CORE}`
		# because if not, then the initramfs layout will be prefixed with
		# the ${TMP_CORE} path.
		cd ${TMP_CORE}

		find . -print0 | cpio -o --null --format=newc | gzip -9 > ${HOME}/${INITRD}

		if [ ! -f "${HOME}/${INITRD}" ]; then
			die "Error creating initramfs file.. exiting"
		fi
	fi
}

# Clean up and exit after a successful build
clean_exit()
{
	clean && einfo "Complete :)"

	if [ "${ZFS_SRM}" != "1" ]; then
		einfo "Please copy the ${INITRD} to your /boot directory"
	fi

	exit 0
}

# Checks to see if the preliminary binaries exist
check_prelim_binaries()
{
	einfo "Checking preliminary binaries..."

	for x in ${PREL_BIN}; do	
		if [ ! -f "${x}" ]; then

			if [ "${x}" = "/bin/cpio" ]; then
				err_bin_dexi ${x} "app-arch/cpio"
			fi

			if [ "${ZFS_SRM}" = "1" ]; then
				if [ "${x}" = "/usr/bin/mksquashfs" ]; then
					err_bin_dexi ${x} "sys-fs/squashfs-tools"
				fi
			fi
		fi
	done
}

# Utility Functions

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

# Used for options
eopt()
{
        echo -e "\e[1;36m>>\e[0;m ${@}"
}

# Used for errors
die()
{
        eline && echo -e "\e[1;31m>>>\e[0;m ${@}" && clean && eline && exit
}

# Prints empty line
eline()
{
	echo ""
}

# Some error functions (Binary doesn't exist)
err_bin_dexi()
{
	if [ ! -z "${2}" ]; then
		die "Binary: ${1} doesn't exist. Please emerge ${2}. Qutting!"
	else
		die "Binary: ${1} doesn't exist. Quitting!"
	fi
}

# Some error functions (Module doesn't exist)
err_mod_dexi()
{
	die "Module: ${1} doesn't exist. Quitting!"
}

# Prints an error message with parameter value
err()
{
        eline && die "Error: ${1}"
}

# Prints wide error messages
werr()
{
	eline && echo "##### ${1} #####" && eline && exit
}

# Copies functions with specific flags
ecp()
{
	cp -afL ${1} ${2} ${3}
}

# Cleans out directories not needed for the initramfs or srm
strip()
{
	if [ "${ZFS_SRM}" = "1" ]; then
		rm -rf ${TMP_CORE}/{bin,lib,mnt,resources,dev,proc,sys}
	fi
}
