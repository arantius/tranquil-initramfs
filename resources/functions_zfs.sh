# Copyright (C) 2012 Jonathan Vasquez
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Checks to see if the binaries exist
chk_bins()
{
	echo "Checking binaries..." && eline

	for x in ${JV_INIT_BINS}; do	
		if [ ${x} = hostid ]; then
			if [ ! -f "${JV_USR_BIN}/${x}" ]; then
				err_bin_dexi ${x}
			fi
		elif [ ${x} = busybox -o ${x} = zpool_layout ]; then
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
chk_mods()
{
	echo "Checking modules..." && eline

	for x in ${JV_INIT_MODS}; do
		if [ ${x} = "spl" -o ${x} = "splat" ]; then
			if [ ! -f "${MOD_PATH}/addon/spl/${x}/${x}.ko" ]; then
				err_mod_dexi ${x}
			fi
		elif [ ${x} = "zavl" ]; then
			if [ ! -f "${MOD_PATH}/addon/zfs/avl/${x}.ko" ]; then
				err_mod_dexi ${x}
			fi
		elif [ ${x} = "znvpair" ]; then
			if [ ! -f "${MOD_PATH}/addon/zfs/nvpair/${x}.ko" ]; then
				err_mod_dexi ${x}
			fi
		elif [ ${x} = "zunicode" ]; then
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
cp_bins()
{
	echo "Copying binaries..." && eline

	for x in ${JV_INIT_BINS}; do
		if [ ${x} = "hostid" ]; then
			cp ${JV_USR_BIN}/${x} ${JV_LOCAL_BIN}
		elif [ ${x} = "busybox" -o ${x} = "zpool_layout" ]; then
			cp ${JV_BIN}/${x} ${JV_LOCAL_BIN}
		else
			cp ${JV_SBIN}/${x} ${JV_LOCAL_SBIN}
		fi
	done  
}

# Copy the required modules to the initramfs
cp_mods()
{
	echo "Copying modules..." && eline

	for x in ${JV_INIT_MODS}; do
		if [ ${x} = "spl" -o ${x} = "splat" ]; then
			cp ${MOD_PATH}/addon/spl/${x}/${x}.ko ${JV_LOCAL_MOD}
		elif [ ${x} = "zavl" ]; then
			cp ${MOD_PATH}/addon/zfs/avl/${x}.ko ${JV_LOCAL_MOD} 
		elif [ ${x} = "znvpair" ]; then
			cp ${MOD_PATH}/addon/zfs/nvpair/${x}.ko ${JV_LOCAL_MOD}
		elif [ ${x} = "zunicode" ]; then
			cp ${MOD_PATH}/addon/zfs/unicode/${x}.ko ${JV_LOCAL_MOD}
		else 	
			cp ${MOD_PATH}/addon/zfs/${x}/${x}.ko ${JV_LOCAL_MOD}
		fi 
	done
}

# Copy all the dependencies of the binary files into the initramfs
# Break this algorithm into get_deps() and cp_deps()
cp_deps()
{
	echo "Copying dependencies..." && eline

	for x in ${JV_INIT_BINS}; do
		if [ ${x} = "busybox" -o ${x} = "zpool_layout" -o ${x} = "hostid" ]; then
			if [ ${JV_LIB_PATH} = "32" ]; then		
				deps="$(ldd bin/${x} | awk ''${JV_LIB32}' {print $1}' | sed -e "s%${JV_LIB32}%%")"				
			else
				deps="$(ldd bin/${x} | awk ''${JV_LIB64}' {print $1}' | sed -e "s%${JV_LIB64}%%")"	
			fi
		else
			if [ ${JV_LIB_PATH} = "32" ]; then
				deps="$(ldd sbin/${x} | awk ''${JV_LIB32}' {print $1}' | sed -e "s%${JV_LIB32}%%")"
			else
				deps="$(ldd sbin/${x} | awk ''${JV_LIB64}' {print $1}' | sed -e "s%${JV_LIB64}%%")"
			fi
		fi 

		for y in ${deps}; do			
			if [ ${JV_LIB_PATH} = "32" ]; then
				cp -Lf ${JV_LIB32}/${y} ${JV_LOCAL_LIB} 2> /dev/null
			else
				cp -Lf ${JV_LIB64}/${y} ${JV_LOCAL_LIB64} 2> /dev/null
			fi
		done
	done
}
