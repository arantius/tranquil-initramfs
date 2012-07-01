# Copyright (C) 2012 Jonathan Vasquez
#
# This source code is released under the MIT license which can be found
# in the LICENSE file.

# Checks to see if the binaries exist
check_binaries()
{
	echo "Checking binaries..." && eline

	for x in ${JV_INIT_BINS}; do	
		if [ "${x}" = "hostid" ]; then
			if [ ! -f "${JV_USR_BIN}/${x}" ]; then
				err_bin_dexi ${x}
			fi
		elif [ "${x}" = "busybox" ]; then
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

# Function won't be used, but must be declared so script doesn't fail
check_modules()
{
	echo "No modules will be checked..." && eline
}

# Copy the required binary files into the initramfs
copy_binaries()
{
	echo "Copying binaries..." && eline

	for x in ${JV_INIT_BINS}; do
		if [ "${x}" = "hostid" ]; then
			cp ${JV_USR_BIN}/${x} ${JV_LOCAL_BIN}
		elif [ "${x}" = "busybox" ]; then
			cp ${JV_BIN}/${x} ${JV_LOCAL_BIN}
		elif [ "${x}" = "lvm" ]; then
			cp ${JV_SBIN}/${x} ${JV_LOCAL_SBIN}/${x}
		elif [ "${x}" = "lvm.static" ]; then
			cp ${JV_SBIN}/${x} ${JV_LOCAL_SBIN}/${x}
			cd sbin/
			ln -s ${x} ${x%.*} 
			cd ../
		else
			cp ${JV_SBIN}/${x} ${JV_LOCAL_SBIN}
		fi
	done
}

# Function won't be used, but must be declared so script doesn't fail
copy_modules()
{
	echo "No modules will be copied..." && eline
}

# Gather all the dependencies (shared libraries) needed for all binaries
get_deps()
{
	echo "Getting dependencies..." && eline

	for x in ${JV_INIT_BINS}; do
		if [ "${x}" = "busybox" ] || [ "${x}" = "hostid" ]; then
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
