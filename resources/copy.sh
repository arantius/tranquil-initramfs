# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Checks to see if the binaries exist
check_binaries()
{
	einfo "Checking binaries..."

	# Check base binaries (all initramfs have these)
	for x in ${_BASE_BINS}; do
		if [ "${x}" = "busybox" ]; then
			if [ ! -f "${_BIN}/${x}" ]; then
				err_bin_dexi ${x}
			fi
		fi
	done

	if [ "${_USE_ZFS}" = "1" ]; then

		eflag "Using ZFS"

		for x in ${_INIT_BINS}; do	
			if [ "${x}" = "hostid" ]; then
				if [ ! -f "${_USR_BIN}/${x}" ]; then
					err_bin_dexi ${x}
				fi
			elif [ "${x}" = "zpool_layout" ]; then
				if [ ! -f "${_BIN}/${x}" ]; then
					err_bin_dexi ${x}
				fi
			else
				if [ ! -f "${_SBIN}/${x}" ]; then
					err_bin_dexi ${x}
				fi
			fi
		done
	fi

	if [ "${_USE_LUKS}" = "1" ]; then

		eflag "Using LUKS"

		for x in ${_LUKS_BINS}; do
			if [ "${x}" = "cryptsetup" ]; then
				if [ ! -f "${_SBIN}/${x}" ]; then
					err_bin_dexi ${x}
				fi
			fi
		done
	fi
}

# Checks to see if the spl and zfs modules exist
check_modules()
{
	einfo "Checking modules..."

	if [ "${_USE_ZFS}" = "1" ]; then
		for x in ${_ZFS_MODS}; do
			if [ "${x}" = "spl" ] || [ "${x}" = "splat" ]; then
				if [ ! -f "${_MODULES}/addon/spl/${x}/${x}.ko" ]; then
					err_mod_dexi ${x}
				fi
			elif [ "${x}" = "zavl" ]; then
				if [ ! -f "${_MODULES}/addon/zfs/avl/${x}.ko" ]; then
					err_mod_dexi ${x}
				fi
			elif [ "${x}" = "znvpair" ]; then
				if [ ! -f "${_MODULES}/addon/zfs/nvpair/${x}.ko" ]; then
					err_mod_dexi ${x}
				fi
			elif [ "${x}" = "zunicode" ]; then
				if [ ! -f "${_MODULES}/addon/zfs/unicode/${x}.ko" ]; then
					err_mod_dexi ${x}
				fi
			else
				if [ ! -f "${_MODULES}/addon/zfs/${x}/${x}.ko" ]; then
					err_mod_dexi ${x}
				fi
			fi
		done
	fi
}

# Copy the required binary files into the initramfs
copy_binaries()
{
        einfo "Copying binaries..."

	# Copy base binaries (all initramfs have these)
	for x in ${_BASE_BINS}; do
		if [ "${x}" = "busybox" ]; then
			ecp ${_BIN}/${x} ${_LOCAL_BIN}
		fi
	done

	if [ "${_USE_ZFS}" = "1" ]; then
		for x in ${_ZFS_BINS}; do
			if [ "${x}" = "hostid" ]; then
				ecp ${_USR_BIN}/${x} ${_LOCAL_BIN}
			elif [ "${x}" = "zpool_layout" ]; then
				ecp ${_BIN}/${x} ${_LOCAL_BIN}
			else
				ecp ${_SBIN}/${x} ${_LOCAL_SBIN}
			fi
		done  
	fi

	if [ "${_USE_LUKS}" = "1" ]; then
		for x in ${_LUKS_BINS}; do
			ecp ${_SBIN}/${x} ${_LOCAL_SBIN}
		done
	fi
}

# Copy the required modules to the initramfs
copy_modules()
{
        einfo "Copying modules..."

	cd ${_TMP}

	if [ "${_USE_ZFS}" = "1" ]; then
		mkdir ${_LOCAL_MODULES}/addon
		ecp -r ${_MODULES}/addon/spl ${_LOCAL_MODULES}/addon
		ecp -r ${_MODULES}/addon/zfs ${_LOCAL_MODULES}/addon
	fi
}

# Copy the documentation
copy_docs()
{
        einfo "Copying documentation..."

	cd ${_TMP}

	if [ "${_USE_ZFS}" = "1" ]; then
		for x in ${_ZFS_MAN5}; do
			ecp -r ${_MAN5}/${x} ${_LOCAL_MAN5}
		done

		for x in ${_ZFS_MAN8}; do
			ecp -r ${_MAN8}/${x} ${_LOCAL_MAN8}
		done
	fi
}

# Gather all the dependencies (shared libraries) needed for all binaries
# Checks bin/ and sbin/ (in the tempinit after it copied the binaries
get_deps()
{
        einfo "Getting dependencies..."

	# Add interpreter to deps since everything will depend on it
	deps="${_LIB64}/ld-linux-x86-64.so*"

	for x in ${_BASE_BINS}; do
		if [ "${x}" = "busybox" ]; then
			# If our busybox wasn't statically built, we would collect
			# its libraries here. Maybe I can implement this in the
			# future if needed.

			deps="${deps} \
			$(ldd ${_LOCAL_BIN}/${x} | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}')"
		fi
	done

	if [ "${_USE_ZFS}" = "1" ]; then
		for x in ${_ZFS_BINS}; do
			if [ "${x}" = "zpool_layout" ] || [ "${x}" = "hostid" ]; then
				deps="${deps} \
				$(ldd ${_LOCAL_BIN}/${x} | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}')"
			else
				deps="${deps} \
				$(ldd ${_LOCAL_SBIN}/${x} | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}')"
			fi
		done
	fi

	if [ "${_USE_LUKS}" = "1" ]; then
		for x in ${_LUKS_BINS}; do
			# If our luks wasn't statically built, we would collect
			# its libraries here. Maybe I can implement this in the
			# future if needed.

			if [ "${x}" = "cryptsetup" ]; then
				deps="${deps} \
				$(ldd ${_LOCAL_SBIN}/${x} | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}')"
			fi
		done
	fi

	# Clean up the unholy mess
	deps=$(echo ${deps} | tr " " "\n" | sort -d | uniq)
}

# Copy all the dependencies of the binary files into the initramfs
copy_deps()
{
	einfo "Copying dependencies..."

	cd ${_TMP}

	for y in ${deps}; do		
                ecp --parents ${y} . 
        done
}
