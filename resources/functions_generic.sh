# Copyright (C) 2012 Jonathan Vasquez
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Message that will be displayed at the top of the screen
headerMessage() {
    echo "##################################"
    echo "${JV_APP_NAME} ${JV_VERSION}"
    echo "Author: ${JV_CONTACT}"
    echo "Released under the ${JV_LICENSE}"
    echo "##################################\n"
}

# Display the menu
displayMenu() {
	echo "Which initramfs would you like to generate:"
	echo "1. ZFS"
	echo "2. LVM"
	echo "3. RAID"
	echo "4. LVM/RAID"
	echo "5. Exit Program"
	echo ""
	echo -n "Current choice: " && read choice
	
	case ${choice} in
		1)
			echo "ZFS will be generated"
			
			INIT_TYPE="ZFS"
			
			. hooks/hook_zfs.sh
			;;
		2)
			echo "LVM will be generated"
			
			INIT_TYPE="LVM"			
			
			. hooks/hook_lvm.sh
			;;
		3) 
			echo "RAID will be generated" && exit
			;;
		4)
			echo "LVM + RAID will be generated" && exit
			;;
		5)
			exit
			;;
		*)
			echo "Error" && exit
			;;
	esac
}

# Ask the user for the name of the kernel they want to generate an initramfs for
getTargetKernel() {
	echo -n "Please enter kernel name: " && read KERNEL_NAME
	
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

# Check to make sure that there is only 1 parameter for displaying help messages
# or that there is the required amount of parameters to trigger the build
getParameters() {
    if [ ${#} -eq 1 ]; then
        # for loop that checks all parameters matching something
        # i would be the mode, and i+1 would be the mode type
        for X in ${@}; do
            
        if [ "${1}" = "--version" ]; then
            echo "${JV_VERSION}" && exit
        elif [ "${1}" = "--author" ] || [ "${1}" = "-a" ]; then
            echo "${JV_CONTACT}" && exit
        elif [ "${1}" = "--help" ] || [ "${1}" = "-h" ]; then
            echo "${JV_APP_NAME} ${JV_VERSION}"
            echo "By ${JV_CONTACT}"
            echo ""
            echo "Usage: createInit <Kernel Name> <ZFS Pool Name>"
            echo "Example: createInit ${JV_EXAMPLE_KERNEL} rpool"
            echo ""
            echo "-h, --help    - This help screen"
            echo "-a, --author  - Author of Application" && exit
            echo "    --version - Application Version"
        elif [ "${1}" = "--lvm" ]; then
            LVM_RUN=1;
        fi
        done
    elif [ "${#}" -lt 1 ] || [ "${#}" -gt 2 ]; then
        echo "Usage: createInit <Kernel Name> <ZFS Pool Name>. Example: createInit ${JV_EXAMPLE_KERNEL} rpool" && exit
    fi

    # createInit -t zfs/btrfs/lvm/lvm-mdadm -p <zfs_pool_name> or <lvm_volume_group_name>
    # createInit --help
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

	echo "Modules dir: ${JV_LOCAL_MOD}"
    mkdir ${TMPDIR} && cd ${TMPDIR}
    mkdir -p bin sbin proc sys dev etc lib mnt/root ${JV_LOCAL_MOD} 

    # If this computer is 64 bit, then make the lib64 dir as well
    if [ "${JV_LIB_PATH}" = "64" ]; then
        mkdir lib64
    fi
}

# Create the required symlinks to busybox
createSymlinks() {
    echo "Creating symlinks to busybox...\n"

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
