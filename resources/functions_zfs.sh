# Copyright (C) 2012 Jonathan Vasquez
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Checks to see if the binaries exist
checkBinaries() {
    for X in ${JV_INIT_BINS}; do		
        if [ ${X} = hostid ] || [ ${X} = zpool_layout ]; then
            if [ ! -f "${JV_USR_BIN}/${X}" ]; then
                errorBinaryNoExist ${X}
            fi
        elif [ ${X} = busybox ]; then
            #if [ ! -f "${JV_BIN}/${X}" ]; then
            if [ ! -f "${HOME_DIR}/binaries/${X}" ]; then
                #errorBinaryNoExist ${X}
                echo "error"
            else
              echo "Busybox exists"  
            fi
        elif [ ${X} = mount.zfs ]; then
            if [ ! -f "${JV_SBIN}/${X}" ]; then
                errorBinaryNoExist ${X}
            fi
        else
			if [ ! -f "${JV_USR_SBIN}/${X}" ]; then
				errorBinaryNoExist ${X}
			fi
		fi
    done
}

# Checks to see if the spl and zfs modules exist
checkModules() {
    for X in ${JV_INIT_MODS}; do 
        if [ "${X}" = "spl" ] || [ "${X}" = "splat" ]; then
            if [ ! -f "${MOD_PATH}/addon/spl/${X}/${X}.ko" ]; then
                errorModuleNoExist ${X}
            fi
        elif [ "${X}" = "zavl" ]; then
            if [ ! -f "${MOD_PATH}/addon/zfs/avl/${X}.ko" ]; then 
                errorModuleNoExist ${X}
            fi
        elif [ "${X}" = "znvpair" ]; then
            if [ ! -f "${MOD_PATH}/addon/zfs/nvpair/${X}.ko" ]; then 
                errorModuleNoExist ${X}
            fi
        elif [ "${X}" = "zunicode" ]; then
            if [ ! -f "${MOD_PATH}/addon/zfs/unicode/${X}.ko" ]; then 
                errorModuleNoExist ${X}
            fi
        elif [ "${X}" = "zlib" ]; then
			if [ ! -f "${MOD_PATH}/kernel/crypto/${X}.ko.gz" ]; then
				errorModuleNoExist ${X}
			fi
		 elif [ "${X}" = "zlib_deflate" ]; then
			if [ ! -f "${MOD_PATH}/kernel/lib/zlib_deflate/${X}.ko.gz" ]; then
				errorModuleNoExist ${X}
			fi
        else 	
            if [ ! -f "${MOD_PATH}/addon/zfs/${X}/${X}.ko" ]; then 
                errorModuleNoExist ${X}
            fi
        fi
    done
}

# Copy the required binary files into the initramfs
copyBinaries() {
    echo "Copying binaries...\n"

    for X in ${JV_INIT_BINS}; do
	    if [ "${X}" = "hostid" ] || [ "${X}" = "zpool_layout" ]; then
			cp ${JV_USR_BIN}/${X} ${JV_LOCAL_BIN}
	    elif [ "${X}" = "busybox" ]; then
			#cp ${JV_BIN}/${X} ${JV_LOCAL_BIN}
			cp ${HOME_DIR}/binaries/busybox ${JV_LOCAL_BIN}
        elif [ "${X}" = "mount.zfs" ]; then
			cp ${JV_SBIN}/${X} ${JV_LOCAL_SBIN}
	    else
			cp ${JV_USR_SBIN}/${X} ${JV_LOCAL_SBIN}
	    fi
    done
}

# Copy the required modules to the initramfs
copyModules() {
    echo "Copying modules...\n"

    for X in ${JV_INIT_MODS}; do
        if [ "${X}" = "spl" ] || [ "${X}" = "splat" ]; then
	        cp ${MOD_PATH}/addon/spl/${X}/${X}.ko ${JV_LOCAL_MOD}
	    elif [ "${X}" = "zavl" ]; then
		    cp ${MOD_PATH}/addon/zfs/avl/${X}.ko ${JV_LOCAL_MOD} 
	    elif [ "${X}" = "znvpair" ]; then
		    cp ${MOD_PATH}/addon/zfs/nvpair/${X}.ko ${JV_LOCAL_MOD}
	    elif [ "${X}" = "zunicode" ]; then
		    cp ${MOD_PATH}/addon/zfs/unicode/${X}.ko ${JV_LOCAL_MOD}
		elif [ "${X}" = "zlib" ]; then 
			cp ${MOD_PATH}/kernel/crypto/${X}.ko.gz ${JV_LOCAL_MOD}/${X}.ko
		elif [ "${X}" = "zlib_deflate" ]; then 
			cp ${MOD_PATH}/kernel/lib/zlib_deflate/${X}.ko.gz ${JV_LOCAL_MOD}/${X}.ko
	    else 	
		    cp ${MOD_PATH}/addon/zfs/${X}/${X}.ko ${JV_LOCAL_MOD}
	    fi 
    done
}

# Copy all the dependencies of the binary files into the initramfs
copyDependencies() {
    echo "Copying dependencies...\n"

    for X in ${JV_INIT_BINS}; do
    
    
	    if [ "${X}" = "busybox" ] || [ "${X}" = "zpool_layout" ] || [ "${X}" = "hostid" ]; then
			if [ "${X}" = "busybox" ]; then
				echo "Copying busybox libraries - j/k they are static"
				#cp ${HOME_DIR}/libraries/* ${JV_LOCAL_LIB}
			else
				#if [ "${JV_LIB_PATH}" = "32" ]; then
					DEPS="$(ldd bin/${X} | awk ''${JV_LIB32}' {print $1}' | sed -e "s%${JV_LIB32}%%")"
				#else
				   # DEPS="$(ldd bin/${X} | awk ''${JV_LIB64}' {print $1}' | sed -e "s%${JV_LIB64}%%")"
				#fi
			fi
	    else
            #if [ "${JV_LIB_PATH}" = "32" ]; then
		        DEPS="$(ldd sbin/${X} | awk ''${JV_LIB32}' {print $1}' | sed -e "s%${JV_LIB32}%%")"
            #else
		     #   DEPS="$(ldd sbin/${X} | awk ''${JV_LIB64}' {print $1}' | sed -e "s%${JV_LIB64}%%")"
            #fi
	    fi 

		# Copy dependencies for each bin specifically, while redirecting error messages
		# (for libraries in locations that don't exist)
	    for Y in ${DEPS}; do
           # if [ "${JV_LIB_PATH}" = "32" ]; then
           echo "Copying ${Y} to ${JV_LOCAL_LIB}"
		        cp -Lf ${JV_LIB32}/${Y} ${JV_LOCAL_LIB} 2> /dev/null
		        cp -Lf ${JV_USR_LIB}/${Y} ${JV_LOCAL_LIB} 2> /dev/null
            #else
		     #   cp -Lf ${JV_LIB64}/${Y} ${JV_LOCAL_LIB64}
		      #  cp -Lf ${JV_USR_LIB}/${Y} ${JV_LOCAL_LIB64}
            #fi
	    done
    done
}

# Create the empty mtab file in /etc and copy the init file into the initramfs
# also sed will modify the initramfs to add the modules directory and zfs pool name
configureInit() {
    echo "Making mtab, and creating/configuring init...\n"

    touch etc/mtab

    if [ ! -f "etc/mtab" ]; then
        echo "Error created mtab file.. exiting\n" && cleanUp && exit
    fi

    # Copy the init script
    cd ${TMPDIR} && cp ${HOME_DIR}/files/${INIT_FILE} init

    # Substitute correct values in using % as delimeter
    # to avoid the slashes in the MOD_PATH [/lib/modules...]
    sed -i -e '9s%""%"'${ZFS_POOL_NAME}'"%' -e '10s%""%"'${MOD_PATH}'"%' init

    if [ ! -f "init" ]; then
        echo "Error created init file.. exiting\n" && cleanUp && exit
    fi
}
