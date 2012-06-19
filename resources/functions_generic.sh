# Copyright (C) 2012 Jonathan Vasquez
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Message that will be displayed at the top of the screen
headerMessage() {
    echo "##################################"
    echo "${JV_APP_NAME} ${JV_VERSION} - ${JV_DISTRO}"
    echo "Author: ${JV_CONTACT}"
    echo "Released under the ${JV_LICENSE}"
    echo "##################################\n"
}

# Display the menu
displayMenu() {
	echo "Which initramfs would you like to generate:"
	echo "1. ZFS"
	echo "2. LVM"
	#echo "3. RAID"
	#echo "4. LVM/RAID"
	echo "3. Exit Program"
	echo ""
	echo -n "Current choice: " && read choice
	echo ""
	
	case ${choice} in
		1)
			echo "ZFS will be generated"
			
			INIT_TYPE="ZFS" && echo ""
			
			. hooks/hook_zfs.sh
			;;
		2)
			echo "LVM will be generated"
			
			INIT_TYPE="LVM" && echo ""	
			
			. hooks/hook_lvm.sh
			;;
		#3) 
			# This option will be implemented in the future
			#echo "RAID creation isn't supported at the moment. Sorry for the inconvenience." && exit
			
			#INIT_TYPE="RAID"
			#
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

# Ask the user for the name of the kernel they want to generate an initramfs for
getTargetKernel() {
	echo -n "Please enter kernel name: " && read KERNEL_NAME && echo ""
	
	# Set modules path to correct location
	MOD_PATH="/lib/modules/${KERNEL_NAME}/"
	JV_LOCAL_MOD="lib/modules/${KERNEL_NAME}/"
}

# Message for displaying the generating event
startMessage() {
    echo "Generating initramfs for ${KERNEL_NAME}\n"
}

# Some error functions
errorBinaryNoExist() {
    echo "Binary: ${1} doesn't exist. Quitting!" && cleanUp && exit
}

errorModuleNoExist() {
    echo "Module: ${1} doesn't exist. Quitting!" && cleanUp && exit
}

# Check to see if "${TMPDIR}" exists, if it does, delete it for a fresh start
# Utility function to return back to home dir and clean up. For exiting on errors
cleanUp() {
    cd ${HOME_DIR}

    if [ -d ${TMPDIR} ]; then
        rm -rf ${TMPDIR}
        
        if [ -d ${TMPDIR} ]; then
            echo "Failed to delete the directory. Exiting..." && exit
        fi
    fi
}

# If x86_64 then use lib64 libraries, else use 32 bit
getArchitecture() {
    case ${JV_CARCH} in
    x86_64)
        JV_LIB_PATH=64
        echo "Detected ${JV_LIB_PATH} bit platform\n"
        ;;
    i[3-6]86)
        JV_LIB_PATH=32
        echo "Detected ${JV_LIB_PATH} bit platform\n"
        ;;
    *)
        echo "Your architecture isn't supported, exiting\n" && cleanUp && exit
        ;;
    esac
}

# Check to make sure kernel modules directory exists
checkForModulesDir() {
    echo "Checking to see if modules directory exists for ${KERNEL_NAME}\n"

    if [ ! -d ${MOD_PATH} ]; then
        echo "Kernel modules directory doesn't exist for ${KERNEL_NAME}. Quitting\n" && exit
    fi
}

# Create the base directory structure for the initramfs
createDirectoryStructure() {
    echo "Creating directory structure for initramfs\n"

    mkdir ${TMPDIR} && cd ${TMPDIR}
    mkdir -p bin sbin proc sys dev etc lib mnt/root ${JV_LOCAL_MOD} 

    # If this computer is 64 bit, then make the lib64 dir as well
    if [ "${JV_LIB_PATH}" = "64" ]; then
        mkdir lib64
    fi
}

# Copy busybox into the initrd and create the required symlinks to it
createSymlinks() {
    echo "Copying busybox and creating symlinks to it..\n"

    cd ${TMPDIR}/${JV_LOCAL_BIN} 
    
    for BB in ${BUSYBOX_TARGETS}; do
        if [ -L "${BB}" ]; then
            echo "${BB} link exists.. removing it\n"
            rm ${BB}
        fi

	    ln -s busybox ${BB}

        if [ ! -L "${BB}" ]; then
            echo "error creating link from ${BB} to busybox\n"
        fi
    done

    cd ${TMPDIR} 
}

# Create and compress the initramfs
createInitramfs() {
    echo "Creating initramfs...\n"

    find . -print0 | cpio -o --null --format=newc | gzip -9 > ${HOME_DIR}/${INIT_TYPE}-${KERNEL_NAME}.img

    if [ ! -f ${HOME_DIR}/${INIT_TYPE}-${KERNEL_NAME}.img ]; then
        echo "Error creating initramfs file.. exiting" && cleanUp && exit
    fi
    
    echo ""
}

# Clean up and exit after a successful build
cleanComplete() {
    cleanUp

    echo "Complete :)\n"

    echo "Please copy the ${INIT_TYPE}-${KERNEL_NAME}.img to your /boot directory\n"

    exit 0
}
