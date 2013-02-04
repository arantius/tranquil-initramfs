# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# This Source Code Form is "Incompatible With Secondary Licenses", as
# defined by the Mozilla Public License, v. 2.0.

# Message that will be displayed at the top of the screen
print_header()
{
	echo -e "-----------------------------------"
	echo -e "\e[38;5;228m| ${_NAME} - v${_VERSION}\e[0;m"
	echo -e "\e[38;5;229m| Author: ${_CONTACT}\e[0;m"
	echo -e "\e[38;5;230m| Distributed under the ${_LICENSE}\e[0;m"
	echo -e "-----------------------------------"
}

# Display the menu
print_menu()
{
	# Check to see if a menu option was passed
	if [ -z "${_CHOICE}" ]; then
		einfo "Which initramfs would you like to generate:"
		eline
		print_options
		eqst "Current choice [1]: " && read _CHOICE
	fi

	case ${_CHOICE} in
	1|"")
		einfo "An initramfs for ZFS will be generated!"
		. hooks/base.sh
		. hooks/zfs.sh
		;;
        2)
                einfo "An initramfs for LUKS + ZFS will be generated!"
		. hooks/base.sh
		. hooks/zfs.sh
                . hooks/luks.sh
                ;;
	3)
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
	eopt "1. ZFS - System Rescue Module"
	eopt "2. Back"
	eopt "3. Exit Program"
	eqst "Current choice [1]: " && read _CHOICE

	case ${_CHOICE} in
	1|"")
		einfo "Creating a ZFS System Rescue Module!"
		. hooks/srm/zfs_srm.sh
		. hooks/zfs.sh
		;;
	2)
		unset _CHOICE
		clear
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
	case ${_ARCH} in
	x86_64)
		_LIB_PATH="64"
		einfo "Detected ${_LIB_PATH} bit platform"
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
	if [ "${_USE_MODULES}" = "1" ]; then
		# Check to see if a kernel was passed
		if [ -z "${_KERNEL}" ]; then
			eqst "Do you want to use the current kernel: $(uname -r)? [Y/n]: " && read _CHOICE

			case ${_CHOICE} in
			y|Y|"")
				_KERNEL=$(uname -r)
				;;
			n|N)
				eqst "Please enter the kernel name: " && read _KERNEL
				;;
			*)
				die "Invalid option, re-open the application"
				;;
			esac
		fi
	fi

	# Set modules path to correct location and sets kernel name for initramfs
	if [ "${_ZFS_SRM}" = "1" ]; then
		_MODULES="/lib/modules/${_KERNEL}/"
		_LOCAL_MODULES="${_TMP}/lib64/modules/${_KERNEL}/"
		_SRM="zfs-${_KERNEL}.srm"
	elif [ "${_USE_MODULES}" = "1" ]; then
		_MODULES="/lib/modules/${_KERNEL}/"
		_LOCAL_MODULES="${_TMP}/lib/modules/${_KERNEL}/"
		_INITRD="initrd-${_KERNEL}.img"
	fi
}


# Message for displaying the generating event
print_start()
{
	if [ "${_ZFS_SRM}" = "1" ]; then
		einfo "Creating ZFS System Rescue Module for ${_KERNEL}..."
	else
		einfo "Creating initramfs for ${_KERNEL}..."
	fi
}


# Check to see if "${_TMP}" exists, if it does, delete it for a fresh start
# Utility function to return back to home dir and clean up. For exiting on errors
clean()
{
	cd ${_HOME}

	if [ -d ${_TMP} ]; then
		rm -rf ${_TMP}

		if [ -d ${_TMP} ]; then
			echo "Failed to delete the directory. Exiting..." && exit
		fi
	fi
}


# Check to make sure kernel modules directory exists
check_mods_dir()
{
	if [ "${_USE_MODULES}" = "1" ]; then
		einfo "Checking to see if modules directory exists for ${_KERNEL}..."

		if [ ! -d "${_MODULES}" ]; then
			die "Kernel modules directory doesn't exist for ${_KERNEL}. Exiting..."
		fi
	fi
}

# Create the base directory structure for the initramfs
create_dirs()
{
	einfo "Creating directory structure for initramfs..."

	# Make base directories
	mkdir ${_TMP} && cd ${_TMP} && mkdir -p ${_CDIRS}

	# Make kernel modules directory
	if [ ! -z ${_LOCAL_MODULES} ] && [ "${_USE_MODULES}" = "1" ]; then
		mkdir -p ${_LOCAL_MODULES}
	fi

	# Make ZFS specific directories
	if [ "${_USE_ZFS}" = "1" ]; then
		mkdir -p etc/zfs
	fi

	# Delete any directories not needed
	strip
}

# Create the required symlinks to it
create_links()
{
	if [ "${_USE_BASE}" = "1" ]; then
		einfo "Creating symlinks to Busybox..."

		cd ${_LOCAL_BIN}

		for bb in ${_BUSYBOX_LN}; do

			if [ -L "${bb}" ]; then
				ewarn "${bb} link exists.. removing it" && eline
				rm ${bb}
			fi

			ln -s busybox ${bb}

			if [ ! -L "${bb}" ]; then
				die "Error creating link from ${bb} to busybox"
			fi
		done

		cd ${_TMP}
	fi
}

# This function copies and sets up any files needed. mtab, init, zpool.cache
config_files()
{
	einfo "Configuring files..."

	cd ${_TMP}

	touch etc/mtab

	if [ ! -f "etc/mtab" ]; then
		die "Error created mtab file... Exiting"
	fi

	if [ "${_ZFS_SRM}" != "1" ]; then
		# Copy init functions
		cp -r ${_HOME}/files/resources/* resources/
		
		# Copy the init script
		cp ${_HOME}/files/init . 

		# Give execute permission to the script
		chmod u+x init

		if [ ! -f "init" ]; then
			die "Error creating init file... Exiting"
		fi
	fi
	
	# Any last substitions or additions/modifications should be done here
	if [ "${_USE_ZFS}" = "1" ] && [ "${_ZFS_SRM}" != "1" ]; then
		# Enable ZFS in the init if ZFS is being used.
		sed -i -e '19s/0/1/' init

		# Copies zpool.cache if it exists
		if [ -f "${_ZCACHE}" ]; then
			cp ${_ZCACHE} etc/zfs
		else
			ewarn "Creating initramfs without zpool.cache"
		fi
	fi

	# Enable LUKS in the init if LUKS is being used.
	if [ "${_USE_LUKS}" = "1" ]; then
		sed -i -e '20s/0/1/' init
	fi
}

# Compresses the kernel modules and generates modprobe table
do_modules()
{
	if [ "${_USE_MODULES}" = "1" ]; then
		einfo "Compressing kernel modules..."

		cd ${_LOCAL_MODULES}

		for module in $(find . -name "*.ko"); do
			gzip ${module}
		done
		
		if [ "${_ZFS_SRM}" != "1" ]; then
			einfo "Generating modprobe information..."
			
			cd ${_TMP}

			depmod -b . ${_KERNEL} || die "You don't have depmod? Something is seriously wrong!"
		fi
	fi
}

# Create the solution
create()
{
	cd ${_TMP}

	if [ "${_ZFS_SRM}" = "1" ]; then
		einfo "Creating and Packing SRM..."

		mksquashfs . ${_HOME}/${_SRM} -all-root -comp xz -noappend -no-progress | logger

		if [ ! -f "${_HOME}/${_SRM}" ]; then
			die "Error creating the SRM file.. exiting"
		fi

		md5sum ${_HOME}/${_SRM} > ${_HOME}/${_SRM%.srm}.md5
	else
		einfo "Creating and Packing initramfs..."

		find . -print0 | cpio -o --null --format=newc | gzip -9 > ${_HOME}/${_INITRD}

		if [ ! -f "${_HOME}/${_INITRD}" ]; then
			die "Error creating initramfs file.. exiting"
		fi
	fi
}

# Clean up and exit after a successful build
clean_exit()
{
	clean

	einfo "Complete :)"

	if [ "${_ZFS_SRM}" != "1" ]; then
		einfo "Please copy the ${_INITRD} to your /boot directory"
	fi

	exit 0
}

# Checks to see if the preliminary binaries exist
check_prelim_binaries()
{
	einfo "Checking preliminary binaries..."

	for x in ${_PREL_BIN}; do	

		if [ ! -f "${x}" ]; then

			if [ "${x}" = "/bin/cpio" ]; then
				err_bin_dexi ${x} "app-arch/cpio"
			fi

			if [ "${_ZFS_SRM}" = "1" ]; then
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
        eline && echo -e "\e[38;5;120m>\e[38;5;119m>\e[38;5;118m>\e[0;m ${@}"
}

# Used for input (questions)
eqst()
{
        eline && echo -en "\e[38;5;195m>\e[38;5;194m>\e[38;5;193m>\e[0;m ${@}"
}

# Used for warnings
ewarn()
{
        eline && echo -e "\e[38;5;229m>\e[38;5;228m>\e[38;5;227m>\e[0;m ${@}"
}

# Used for flags
eflag()
{
        eline && echo -e "\e[38;5;99m>\e[38;5;98m>\e[38;5;97m>\e[0;m ${@}"
}

# Used for options
eopt()
{
        echo -e "\e[38;5;81m>\e[38;5;80m>\e[0;m ${@}"
}

# Used for errors
die()
{
        eline && echo -e "\e[38;5;160m>\e[38;5;124m>\e[38;5;88m>\e[0;m ${@}" && clean && eline && exit
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

err_mod_dexi()
{
	die "Module: ${1} doesn't exist. Quitting!"
}

# Prints an error message with parameter value
err()
{
        eline && die "Error: ${1}"
}

werr()
{
	eline
        echo "##### ${1} #####"
	eline
	exit
}

# Copies functions with specific flags
ecp()
{
	cp -afL ${1} ${2} ${3}
}

# Cleans out directories not needed for the initramfs or srm
strip()
{
	if [ "${_ZFS_SRM}" = "1" ]; then
		rm -rf ${_TMP}/{bin,lib,mnt,resources,dev,proc,sys}
	fi
}
