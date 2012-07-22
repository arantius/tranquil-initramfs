# Copyright (C) 2012 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# Distributed under the ISC license which can be found in the LICENSE file.

# Checks to see if the binaries exist
check_binaries()
{
	echo "Checking binaries..." && eline

	for x in ${JV_INIT_BINS}; do	
		if [ "${x}" = "hostid" ]; then
			if [ ! -f "${JV_USR_BIN}/${x}" ]; then
				err_bin_dexi ${x}
			fi
		elif [ "${x}" = "busybox" ] || [ "${x}" = "zpool_layout" ]; then
			if [ ! -f "${JV_BIN}/${x}" ]; then
				err_bin_dexi ${x}
			fi
		else
			if [ ! -f "${JV_SBIN}/${x}" ]; then
				err_bin_dexi ${x}
			fi
		fi
	done
}

# Checks to see if the spl and zfs modules exist
check_modules()
{
	echo "Checking modules..." && eline

	for x in ${JV_INIT_MODS}; do
		if [ "${x}" = "spl" ] || [ "${x}" = "splat" ]; then
			if [ ! -f "${MOD_PATH}/addon/spl/${x}/${x}.ko" ]; then
				err_mod_dexi ${x}
			fi
		elif [ "${x}" = "zavl" ]; then
			if [ ! -f "${MOD_PATH}/addon/zfs/avl/${x}.ko" ]; then
				err_mod_dexi ${x}
			fi
		elif [ "${x}" = "znvpair" ]; then
			if [ ! -f "${MOD_PATH}/addon/zfs/nvpair/${x}.ko" ]; then
				err_mod_dexi ${x}
			fi
		elif [ "${x}" = "zunicode" ]; then
			if [ ! -f "${MOD_PATH}/addon/zfs/unicode/${x}.ko" ]; then
				err_mod_dexi ${x}
			fi
		else
			if [ ! -f "${MOD_PATH}/addon/zfs/${x}/${x}.ko" ]; then
				err_mod_dexi ${x}
			fi
		fi
	done
}

# Copy the required binary files into the initramfs
copy_binaries()
{
	echo "Copying binaries..." && eline

	for x in ${JV_INIT_BINS}; do
		if [ "${x}" = "hostid" ]; then
			cp ${JV_USR_BIN}/${x} ${JV_LOCAL_BIN}
		elif [ "${x}" = "busybox" ] || [ "${x}" = "zpool_layout" ]; then
			cp ${JV_BIN}/${x} ${JV_LOCAL_BIN}
		else
			cp ${JV_SBIN}/${x} ${JV_LOCAL_SBIN}
		fi
	done  
}

# Copy the required modules to the initramfs
copy_modules()
{
	echo "Copying modules..." && eline

	for x in ${JV_INIT_MODS}; do
		if [ "${x}" = "spl" ] || [ "${x}" = "splat" ]; then
			cp ${MOD_PATH}/addon/spl/${x}/${x}.ko ${JV_LOCAL_MOD}
		elif [ "${x}" = "zavl" ]; then
			cp ${MOD_PATH}/addon/zfs/avl/${x}.ko ${JV_LOCAL_MOD} 
		elif [ "${x}" = "znvpair" ]; then
			cp ${MOD_PATH}/addon/zfs/nvpair/${x}.ko ${JV_LOCAL_MOD}
		elif [ "${x}" = "zunicode" ]; then
			cp ${MOD_PATH}/addon/zfs/unicode/${x}.ko ${JV_LOCAL_MOD}
		else 	
			cp ${MOD_PATH}/addon/zfs/${x}/${x}.ko ${JV_LOCAL_MOD}
		fi 
	done
}

# Gather all the dependencies (shared libraries) needed for all binaries
get_deps()
{
	echo "Getting dependencies..." && eline

	for x in ${JV_INIT_BINS}; do
		if [ "${x}" = "busybox" ] || [ "${x}" = "zpool_layout" ] || [ "${x}" = "hostid" ]; then
			if [ "${JV_LIB_PATH}" = "32" ]; then
				deps=${deps}" ""$(ldd bin/${x} | awk ''${JV_LIB32}' {print $1}' | sed -e "s%${JV_LIB32}%%")"				
			else
				deps=${deps}" ""$(ldd bin/${x} | awk ''${JV_LIB64}' {print $1}' | sed -e "s%${JV_LIB64}%%")"	
			fi
		else
			if [ "${JV_LIB_PATH}" = "32" ]; then
				deps=${deps}" ""$(ldd sbin/${x} | awk ''${JV_LIB32}' {print $1}' | sed -e "s%${JV_LIB32}%%")"
			else
				deps=${deps}" ""$(ldd sbin/${x} | awk ''${JV_LIB64}' {print $1}' | sed -e "s%${JV_LIB64}%%")"
			fi
		fi
	done
}

