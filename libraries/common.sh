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
	if [[ -z ${CHOICE} ]]; then
		einfo "Which initramfs would you like to generate:"
		print_options
		eqst "Current choice [1]: " && read CHOICE
	fi

	case ${CHOICE} in
	1|"")
		. hooks/base.sh
		. hooks/zfs.sh
		. hooks/addon.sh
		;;
        2)
		. hooks/base.sh
		. hooks/zfs.sh
                . hooks/luks.sh
		. hooks/addon.sh
                ;;
	*)
		eline && ewarn "Exiting." && exit
		;;
	esac
}

# Makes sure that arch is x86_64
get_arch()
{
        if [[ ${ARCH} != "x86_64" ]]; then
		die "Your architecture isn't supported, exiting"
        fi
}

# Prints the available options if the user passes an invalid number
print_options()
{
	eline
	eopt "1. ZFS"
	eopt "2. Encrypted ZFS (LUKS + ZFS)"
	eopt "3. Exit Program"
	eline
}

# Ask the user if they want to use their current kernel, or another one
do_kernel()
{
        # Check to see if a kernel was passed
        if [[ -z ${KERNEL} ]]; then
                eline && eqst "Do you want to use the current kernel: $(uname -r)? [Y/n]: " && read CHOICE && eline

                case ${CHOICE} in
                y|Y|"")
                        KERNEL=$(uname -r)
                        ;;
                n|N)
                        eqst "Please enter the kernel name: " && read KERNEL && eline

                        if [[ -z ${KERNEL} ]]; then
                                die "You didn't enter a kernel. Exiting..."
                        fi

                        ;;
                *)
                        die "Invalid option. Exiting..."
                        ;;
                esac
        fi

	# Set modules path to correct location and sets kernel name for initramfs
        MODULES="/lib/modules/${KERNEL}/"
        LMODULES="${T}/${MODULES}"
        INITRD="initrd-${KERNEL}"

	# Check modules directory
	check_mods_dir
}

# Message for displaying the generating event
print_start()
{
	eline && einfo "[ Starting ]" && eline
	einfo "Creating initramfs for ${KERNEL}..."
}

# Check to see if ${T} exists, if it does, delete it for a fresh start
# Utility function to return back to home dir and clean up. For exiting on errors
clean()
{
	# Go back to the original working directory so that we are
	# completely sure that there will be no inteference cleaning up.
	cd ${H}

	if [[ -d ${T} ]]; then
		rm -rf ${T}

		if [[ -d ${T} ]]; then
			echo "Failed to delete the ${T} directory. Exiting..." && exit
		fi
	fi
}

# Check to make sure kernel modules directory exists
check_mods_dir()
{
        einfo "Checking to see if ${MODULES} exists..."

        if [[ ! -d ${MODULES} ]]; then
                die "The kernel modules directory for ${KERNEL} doesn't exist. Exiting..."
        fi
}

# Create the base directory structure for the initramfs
create_dirs()
{
	einfo "Creating directory structure for initramfs..."

	# Make base directories
	mkdir ${T} && mkdir -p ${CDIRS}

	# Make kernel modules directory
	if [[ ! -z ${LMODULES} ]]; then
		mkdir -p ${LMODULES}
	fi

	# Make ZFS specific directories
	if [[ ${USE_ZFS} == "1" ]]; then
		mkdir -p ${T}/etc/zfs
	fi

	# Make LUKS specific directories
	if [[ ${USE_LUKS} == "1" ]]; then
		mkdir -p ${T}/mnt/key
	fi
}

# Create the required symlinks to it
create_links()
{
	if [[ ${USE_BASE} == "1" ]]; then
		einfo "Creating symlinks..."
	
		# Needs to be from this directory so that the links are relative
		cd ${LBIN}

		# Create 'sh' symlink to 'bash'
		if [[ -L sh ]]; then
			rm sh
		fi

		ln -s bash sh

		if [[ ! -L sh ]]; then
			die "Error creating link from sh to bash"
		fi

		# Create busybox links
		${LBIN}/busybox --install  .

		# Go to the directory where kmod is in
		if [[ -f ${LSBIN}/kmod ]]; then
			cd ${LSBIN}
		elif [[ -f ${LBIN}/kmod ]]; then
			cd ${LBIN}
		fi
		
		# Remove the busybox equivalent
		for i in ${KMOD_SYM}; do
			rm ${LBIN}/${i}
			ln -s kmod ${i}
		done
	fi
}

# This function copies and sets up any files needed. mtab, init, zpool.cache
config_files()
{
	einfo "Configuring files..."

	touch ${T}/etc/mtab

	if [[ ! -f ${T}/etc/mtab ]]; then
		die "Error created mtab file... Exiting"
	fi

        # Copy init functions
        cp -r ${H}/files/libraries/* ${T}/libraries/
        
        # Copy the init script
        cp ${H}/files/init ${T} 

        # Give execute permission to the script
        chmod u+x ${T}/init

        if [[ ! -f ${T}/init ]]; then
                die "Error creating init file... Exiting"
        fi

	# Any last substitions or additions/modifications should be done here
	if [[ ${USE_ZFS} == "1" ]]; then
		# Enable ZFS in the init if ZFS is being used.
		sed -i -e "13s/0/1/" ${T}/init

		# Sets initramfs script version number
		sed -i -e "16s/0/${VERSION}/" ${T}/init

		# Copy the /etc/modprobe.d/zfs.conf file if it exists
		if [[ -f "/etc/modprobe.d/zfs.conf" ]]; then
			mkdir ${T}/etc/modprobe.d/
			cp /etc/modprobe.d/zfs.conf ${T}/etc/modprobe.d/
		fi
	fi

	# Enable LUKS in the init if LUKS is being used.
	if [[ ${USE_LUKS} == "1" ]]; then
		sed -i -e "14s/0/1/" ${T}/init
	fi

	# Plug in the modules that the user wants to load
	if [[ ${USE_ADDON} == "1" ]]; then
		sed -i -e "18s/\"\"/\"${ADDON_MODS}\"/" ${T}/libraries/common.sh
	fi
}

# Compresses the kernel modules and generates modprobe table
do_modules()
{
        einfo "Compressing kernel modules..."

        for x in $(find ${LMODULES} -name "*.ko"); do
                gzip ${x}
        done
        
        einfo "Generating modprobe information..."
        
        # Copy modules.order and modules.builtin just so depmod doesn't spit out warnings. -_-
        cp -a ${MODULES}/modules.{order,builtin} ${LMODULES}

        depmod -b ${T} ${KERNEL} || die "You don't have depmod? Something is seriously wrong!"
}

# Create the solution
create()
{
        einfo "Creating and Packing initramfs..."

        # The find command must use the `find .` and not `find ${T}`
        # because if not, then the initramfs layout will be prefixed with
        # the ${T} path.
        cd ${T}

        find . -print0 | cpio -o --null --format=newc | gzip -9 > ${H}/${INITRD}

        if [[ ! -f ${H}/${INITRD} ]]; then
                die "Error creating initramfs file.. exiting"
        fi
}

# Clean up and exit after a successful build
clean_exit()
{
	eline && einfo "[ Ending ]" && eline && clean
	einfo "Please copy the ${INITRD} to your /boot directory"
	exit 0
}

# Checks to see if the preliminary binaries exist
check_prelim_binaries()
{
	einfo "Checking preliminary binaries..."

	for x in ${PREL_BIN}; do	
		if [[ ! -f ${x} ]]; then
			if [[ ${x} == "/bin/cpio" ]]; then
				err_bin_dexi ${x} "app-arch/cpio"
			fi
		fi
	done
}

# Utility Functions

# Used for displaying information
einfo()
{
        echo -e "\e[1;32m>>>\e[0;m ${@}"
}

# Used for input (questions)
eqst()
{
        echo -en "\e[1;37m>>>\e[0;m ${@}"
}

# Used for warnings
ewarn()
{
        echo -e "\e[1;33m>>>\e[0;m ${@}"
}

# Used for flags
eflag()
{
        echo -e "\e[1;34m>>>\e[0;m ${@}"
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
	if [[ ! -z ${2} ]]; then
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
