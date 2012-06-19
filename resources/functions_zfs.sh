# Copyright (C) 2012 Jonathan Vasquez
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Checks to see if the binaries exist
checkBinaries() {
	echo "Checking binaries..." && eline
	
    for X in ${JV_INIT_BINS}; do		
        if [ ${X} = hostid ] ; then
            if [ ! -f "${JV_USR_BIN}/${X}" ]; then
                errorBinaryNoExist ${X}
            fi
        elif [ ${X} = busybox ] || [ ${X} = zpool_layout ]; then
            if [ ! -f "${JV_BIN}/${X}" ]; then
                errorBinaryNoExist ${X}
            fi
        else
			if [ ! -f "${JV_SBIN}/${X}" ]; then
                errorBinaryNoExist ${X}
            fi
		fi
    done
}

# Checks to see if the spl and zfs modules exist
checkModules() {
	echo "Copying modules..." && eline
	
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
        else 	
            if [ ! -f "${MOD_PATH}/addon/zfs/${X}/${X}.ko" ]; then 
                errorModuleNoExist ${X}
            fi
        fi
    done
}

# Copy the required binary files into the initramfs
copyBinaries() {
    echo "Copying binaries..." && eline

    for X in ${JV_INIT_BINS}; do
	    if [ "${X}" = "hostid" ]; then
			cp ${JV_USR_BIN}/${X} ${JV_LOCAL_BIN}
	    elif [ "${X}" = "busybox" ] || [ "${X}" = "zpool_layout" ]; then
			cp ${JV_BIN}/${X} ${JV_LOCAL_BIN}
	    else
			cp ${JV_SBIN}/${X} ${JV_LOCAL_SBIN}
	    fi
    done  
}

# Copy the required modules to the initramfs
copyModules() {
    echo "Copying modules..." && eline

    for X in ${JV_INIT_MODS}; do
        if [ "${X}" = "spl" ] || [ "${X}" = "splat" ]; then
	        cp ${MOD_PATH}/addon/spl/${X}/${X}.ko ${JV_LOCAL_MOD}
	    elif [ "${X}" = "zavl" ]; then
		    cp ${MOD_PATH}/addon/zfs/avl/${X}.ko ${JV_LOCAL_MOD} 
	    elif [ "${X}" = "znvpair" ]; then
		    cp ${MOD_PATH}/addon/zfs/nvpair/${X}.ko ${JV_LOCAL_MOD}
	    elif [ "${X}" = "zunicode" ]; then
		    cp ${MOD_PATH}/addon/zfs/unicode/${X}.ko ${JV_LOCAL_MOD}
	    else 	
		    cp ${MOD_PATH}/addon/zfs/${X}/${X}.ko ${JV_LOCAL_MOD}
	    fi 
    done
    
    # Compress the copied modules and generate modules.dep
    compressModules && generateModprobe
}

# Copy all the dependencies of the binary files into the initramfs
copyDependencies() {
    echo "Copying dependencies..." && eline
	
    for X in ${JV_INIT_BINS}; do	
    	
	    if [ "${X}" = "busybox" ] || [ "${X}" = "zpool_layout" ] || [ "${X}" = "hostid" ]; then
            if [ "${JV_LIB_PATH}" = "32" ]; then		
		        DEPS="$(ldd bin/${X} | awk ''${JV_LIB32}' {print $1}' | sed -e "s%${JV_LIB32}%%")"				
            else
		        DEPS="$(ldd bin/${X} | awk ''${JV_LIB64}' {print $1}' | sed -e "s%${JV_LIB64}%%")"	
            fi
	    else
            if [ "${JV_LIB_PATH}" = "32" ]; then
		        DEPS="$(ldd sbin/${X} | awk ''${JV_LIB32}' {print $1}' | sed -e "s%${JV_LIB32}%%")"
            else
		        DEPS="$(ldd sbin/${X} | awk ''${JV_LIB64}' {print $1}' | sed -e "s%${JV_LIB64}%%")"
            fi
	    fi 

	    for Y in ${DEPS}; do			
            if [ "${JV_LIB_PATH}" = "32" ]; then
		        cp -Lf ${JV_LIB32}/${Y} ${JV_LOCAL_LIB} 2> /dev/null
            else
		        cp -Lf ${JV_LIB64}/${Y} ${JV_LOCAL_LIB64} 2> /dev/null
            fi
	    done
    done
}
