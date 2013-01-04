# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Message that will be displayed at the top of the screen
print_header()
{
	echo "-----------------------------------"
	echo "| ${_NAME} - v${_VERSION}"
	echo "| Author: ${_CONTACT}"
	echo "| Distributed under the ${_LICENSE}"
	echo "-----------------------------------"
}

# Display the menu
print_menu()
{
	# Check to see if a menu option was passed
	if [ -z "${choice}" ]; then
		einfo "Which initramfs would you like to generate:"
		eopt "1. ZFS"
                eopt "2. Encrypted ZFS (LUKS + ZFS)"
		eopt "3. Exit Program"
		eline
		echo -n "Current choice [1]: " && read choice
	fi

	case ${choice} in
	1|"")
		einfo "An initramfs for ZFS will be generated!"
		. hooks/base.sh
		. hooks/zfs.sh
		;;
        2)
                einfo "An initramfs for LUKS + ZFS will be generated!"
		. hooks/base.sh
		. hooks/zfs.sh
                . hooks/zfs_luks.sh
                ;;
	*)
		ewarn "Exiting." && exit
		;;
	esac
}

# If x86_64 then use lib64 libraries, else if i[*]86, use 32 bit libraries
get_arch()
{
	eline

	case ${_ARCH} in
	x86_64)
		_LIB_PATH="64"
		echo "Detected ${_LIB_PATH} bit platform"
		;;
	i[3-6]86)
		_LIB_PATH="32"
		echo "Detected ${_LIB_PATH} bit platform"
		;;
	*)
		echo "Your architecture isn't supported, exiting" && eline && clean && exit
		;;
	esac
}

# Prints the available options if the user passes an invalid number
print_options()
{
	echo "1. ZFS"
        echo "2. Encrypted ZFS (LUKS + ZFS)"
}

print_usage()
{
	echo "./createInit 1 ${_EXAMPLE_KERNEL}"
}

# Ask the user if they want to use their current kernel, or another one
get_target_kernel()
{
	# Check to see if a kernel wasn passed
	if [ -z "${_KERNEL}" ]; then
		eline

		echo -n "Do you want to use the current kernel: $(uname -r)? [Y/n]: " && read choice
	
		case ${choice} in
		y|Y|"")
			_KERNEL=$(uname -r)
			;;
		n|N)
			eline
			echo -n "Please enter the kernel name: " && read _KERNEL
			;;
		*)
			echo "Invalid option, re-open the application" && exit
			;;
		esac
	fi
}

# Set modules path to correct location and sets kernel name for initramfs
set_target_kernel()
{
	_MODULES="/lib/modules/${_KERNEL}/"
	_LOCAL_MODULES="${_TMP}/lib/modules/${_KERNEL}/"
	_INITRD="initrd-${_KERNEL}.img"
}

# Message for displaying the generating event
print_start()
{
	einfo "Generating initramfs for ${_KERNEL}..."
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
	einfo "Checking to see if modules directory exists for ${_KERNEL}..."

	if [ ! -d "${_MODULES}" ]; then
		die "Kernel modules directory doesn't exist for ${_KERNEL}. Quitting"
	fi
}

# Create the base directory structure for the initramfs
create_dirs()
{
	einfo "Creating directory structure for initramfs..."

	mkdir ${_TMP} && cd ${_TMP} && mkdir -p ${_CDIRS}

	if [ "${_USE_ZFS}" = "1" ]; then
		mkdir -p etc/zfs
	fi

	# If the specific kernel directory doesn't exist in the initramfs 
	# tempdir, then create it
	if [ ! -z ${_LOCAL_MODULES} ]; then
		mkdir -p ${_LOCAL_MODULES}
	fi
}

# Create the required symlinks to it
create_symlinks()
{
	einfo "Creating symlinks to Busybox..."

	cd ${_LOCAL_BIN}

	for bb in ${_BUSYBOX_LN}; do

		if [ -L "${bb}" ]; then
			echo "${bb} link exists.. removing it" && eline
			rm ${bb}
		fi

		ln -s busybox ${bb}

		if [ ! -L "${bb}" ]; then
			die "Error creating link from ${bb} to busybox"
		fi
	done

	cd ${_TMP}
}

# Create the empty mtab file in /etc and copy the init file into the initramfs
# also sed will modify the initramfs to add additional information
config_init()
{
	einfo "Making mtab, and creating/configuring init..."

	cd ${_TMP}

	touch etc/mtab

	if [ ! -f "etc/mtab" ]; then
		die "Error created mtab file.. exiting"
	fi

        # Copy init functions
        cp -r ${_HOME}/files/resources/* resources/
	
        # Copy the init script
	cp ${_HOME}/files/init . 
	
	# Substitute any changes to the init file
	
	# Enable ZFS in the init if ZFS is being used.
	if [ "${_USE_ZFS}" = "1" ]; then
		sed -i -e '16s/0/1/' init
	fi

	# Enable LUKS in the init if LUKS is being used.
	if [ "${_USE_LUKS}" = "1" ]; then
		sed -i -e '17s/0/1/' init
	fi

	# Give execute permission to the script
	chmod u+x init
	
	if [ ! -f "init" ]; then
		die "Error creating init file.. exiting"
	fi
}

# Compresses the kernel modules
pack_modules()
{
        einfo "Compressing kernel modules..."

	cd ${_LOCAL_MODULES}

        for module in $(find . -name "*.ko"); do
		gzip ${module}
        done

        cd ${_TMP}
}

# Generate depmod info
modules_dep()
{
	einfo "Generating modprobe information..."
	
	cd ${_TMP}

	depmod -b . ${_KERNEL} || die "You don't have depmod? Something is seriously wrong!"
}

# Create the initramfs
create_initrd()
{
	einfo "Creating and Packing initramfs..."

	cd ${_TMP}

	find . -print0 | cpio -o --null --format=newc | gzip -9 > ${_HOME}/${_INITRD}

	if [ ! -f "${_HOME}/${_INITRD}" ]; then
		die "Error creating initramfs file.. exiting"
	fi
}

# Clean up and exit after a successful build
clean_all()
{
	clean

	einfo "Complete :)"

	einfo "Please copy the ${_INITRD} to your /boot directory"

	exit 0
}

# Checks to see if the preliminary binaries exist
check_prelim_binaries()
{
	einfo "Checking preliminary binaries..."

	for x in ${_PREL_BIN}; do	
		if [ "${x}" = "cpio" ]; then
			if [ ! -f "${_BIN}/${x}" ]; then
				err_bin_dexi ${x}
			fi
		fi
	done
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
        eline && echo -e "\033[1;31m>>>\033[0;m ${@}" && clean && eline && exit
}

# Prints empty line
eline()
{
	echo ""
}

# Some error functions (Binary doesn't exist)
err_bin_dexi()
{
	die "Binary: ${1} doesn't exist. Quitting!"
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
