# Copyright (C) 2012 Jonathan Vasquez
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Message that will be displayed at the top of the screen
message_header()
{
	echo "##################################"
	echo "${JV_APP_NAME} ${JV_VERSION} - ${JV_DISTRO}"
	echo "Author: ${JV_CONTACT}"
	echo "Released under the ${JV_LICENSE}"
	echo "##################################\n"
}

# Display the menu
display_menu()
{
	echo "Which initramfs would you like to generate:"
	echo "1. ZFS"
	echo "2. LVM"
	#echo "3. RAID"
	#echo "4. LVM/RAID"
	echo "3. Exit Program"
	eline
	echo -n "Current choice: " && read choice
	eline
	
	case ${choice} in
	1)
		echo "An initramfs for ZFS will be generated!"
		. hooks/hook_zfs.sh
		;;
	2)
		echo "An initramfs for LVM will be generated!"
		
		INIT_TYPE="LVM" && eline	
		
		. hooks/hook_lvm.sh
		;;
	#3) 
		# This option will be implemented in the future
		#echo "RAID creation isn't supported at the moment. Sorry for the inconvenience." && exit
		
		#INIT_TYPE="RAID"
		
		#. hooks/hook_raid.sh
		#;;
	#4)
		# This option will be implemented in the future
		#echo "LVM + RAID creation isn't supported at the moment. Sorry for the inconvenience." && exit
		
		#INIT_TYPE="LVM_RAID"
		
		#. hooks/hook_lvm_raid.sh
		#;;
	3)
		exit
		;;
	*)
		echo "Invalid choice. Exiting." && exit
		;;
	esac
}

# Ask the user if they want to use their current kernel, or another one to generate an initramfs for it
get_target_kernel()
{
	echo -n "Do you want to use current kernel: $(uname -r)? [Y/n]: " && read choice && eline
	
	case ${choice} in
	y|Y|"")
		KERNEL_NAME=$(uname -r)
		;;
	n|N)
		echo -n "Please enter kernel name: " && read KERNEL_NAME && eline
		;;
	*)
		echo "Invalid option, re-open the application" && exit
		;;
	esac
	
	# Set modules path to correct location
	MOD_PATH="/lib/modules/${KERNEL_NAME}/"
	JV_LOCAL_MOD="lib/modules/${KERNEL_NAME}/"
}

# Message for displaying the generating event
message_start()
{
	echo "Generating initramfs for ${KERNEL_NAME}..." && eline
}

# Prints empty line
eline()
{
	echo ""
}

# Some error functions (Binary doesn't exist)
err_bin_dexi()
{
	echo "Binary: ${1} doesn't exist. Quitting!" && clean && exit
}

err_mod_dexi()
{
	echo "Module: ${1} doesn't exist. Quitting!" && clean && exit
}

# Check to see if "${TMPDIR}" exists, if it does, delete it for a fresh start
# Utility function to return back to home dir and clean up. For exiting on errors
clean()
{
	cd ${HOME_DIR}

	if [ -d ${TMPDIR} ]; then
		rm -rf ${TMPDIR}

		if [ -d ${TMPDIR} ]; then
			echo "Failed to delete the directory. Exiting..." && exit
		fi
	fi
}

# If x86_64 then use lib64 libraries, else use 32 bit
get_arch()
{
	case ${JV_CARCH} in
	x86_64)
		JV_LIB_PATH=64
		echo "Detected ${JV_LIB_PATH} bit platform" && eline
		;;
	i[3-6]86)
		JV_LIB_PATH=32
		echo "Detected ${JV_LIB_PATH} bit platform" && eline
		;;
	*)
		echo "Your architecture isn't supported, exiting" && eline && clean && exit
		;;
	esac
}

# Check to make sure kernel modules directory exists
chk_mod_dir()
{
	echo "Checking to see if modules directory exists for ${KERNEL_NAME}..." && eline

	if [ ! -d ${MOD_PATH} ]; then
		echo "Kernel modules directory doesn't exist for ${KERNEL_NAME}. Quitting" && eline && exit
	fi
}

# Create the base directory structure for the initramfs
crt_dir_struct()
{
	echo "Creating directory structure for initramfs..." && eline

	mkdir ${TMPDIR} && cd ${TMPDIR}
	mkdir -p bin sbin proc sys dev etc lib mnt/root ${JV_LOCAL_MOD}

	# If this computer is 64 bit, then make the lib64 dir as well
	if [ "${JV_LIB_PATH}" = "64" ]; then
		mkdir lib64
	fi
}

# Create the required symlinks to it
crt_sym()
{
	echo "Creating symlinks to Busybox..." && eline

	cd ${TMPDIR}/${JV_LOCAL_BIN}

	for bb in ${BUSYBOX_TARGETS}; do
		if [ -L "${bb}" ]; then
			echo "${bb} link exists.. removing it" && eline
			rm ${bb}
		fi

		ln -s busybox ${bb}

		if [ ! -L "${bb}" ]; then
			echo "error creating link from ${bb} to busybox" && eline
		fi
	done

	cd ${TMPDIR}
}

# Create the empty mtab file in /etc and copy the init file into the initramfs
# also sed will modify the initramfs to add additional information
conf_init()
{
	echo "Making mtab, and creating/configuring init..." && eline

	touch etc/mtab

	if [ ! -f "etc/mtab" ]; then
		echo "Error created mtab file.. exiting" && eline && exit
	fi

	# Copy the init script
	cd ${TMPDIR} && cp ${HOME_DIR}/files/${INIT_FILE} init

	if [ ! -f "init" ]; then
		echo "Error creating init file.. exiting" && eline && clean && exit
	fi
}

# Compresses the kernel modules
gz_mods()
{
	echo "Compressing kernel modules..." && eline

	cd ${JV_LOCAL_MOD}

	for module in ./*.ko; do
		gzip ${module}
	done

	# Return to original location
	cd ${TMPDIR}
}

# Generate depmod info
gen_depm()
{
	cd ${TMPDIR}

	echo "Generating modprobe information..." && eline

	depmod -b . ${KERNEL_NAME}
}

# Create the initramfs
crt_initrd()
{
	echo "Creating and Packing initramfs..." && eline

	find . -print0 | cpio -o --null --format=newc | gzip -9 > ${HOME_DIR}/${INIT_TYPE}-${KERNEL_NAME}.img

	if [ ! -f ${HOME_DIR}/${INIT_TYPE}-${KERNEL_NAME}.img ]; then
		echo "Error creating initramfs file.. exiting" && clean && exit
	fi

	echo ""
}

# Clean up and exit after a successful build
clean_all()
{
	clean

	echo "Complete :)" && eline

	echo "Please copy the ${INIT_TYPE}-${KERNEL_NAME}.img to your /boot directory" && eline

	exit 0
}
