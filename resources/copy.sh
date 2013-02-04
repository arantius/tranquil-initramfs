# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# This Source Code Form is "Incompatible With Secondary Licenses", as
# defined by the Mozilla Public License, v. 2.0.

# Checks to see if the binaries exist
check_binaries()
{
	einfo "Checking binaries..."

	# Check base binaries (all initramfs have these)
	for x in ${_BASE_BINS}; do
		if [ ! -f "${x}" ]; then
			err_bin_dexi ${x}
		fi
	done

	if [ "${_USE_ZFS}" = "1" ]; then
		eflag "Using ZFS"

		for x in ${_INIT_BINS}; do	
			if [ ! -f "${x}" ]; then
				err_bin_dexi ${x}
			fi
		done
	fi

	if [ "${_USE_LUKS}" = "1" ]; then
		eflag "Using LUKS"

		for x in ${_LUKS_BINS}; do
			if [ ! -f "${x}" ]; then
				err_bin_dexi ${x}
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
			if [ ! -f "${x}" ]; then
				err_mod_dexi ${x}
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
		ecp ${x} ${_TMP}/${x}
	done

	if [ "${_USE_ZFS}" = "1" ]; then
		for x in ${_ZFS_BINS}; do
			ecp ${x} ${_TMP}/${x}
		done  
	fi

	if [ "${_USE_LUKS}" = "1" ]; then
		for x in ${_LUKS_BINS}; do
			ecp ${x} ${_TMP}/${x}
		done
	fi
}

# Copy the required modules to the initramfs
copy_modules()
{
        einfo "Copying modules..."

	cd ${_TMP}

	if [ "${_ZFS_SRM}" = "1" ]; then
		for x in ${_ZFS_MODS}; do 
			local p=$(dirname ${_TMP}/${x} | sed 's:/lib/:/lib64/:')
			mkdir -p ${p} && ecp -r ${x} ${p} 
		done
	elif [ "${_USE_ZFS}" = "1" ]; then
		for x in ${_ZFS_MODS}; do 
			mkdir -p "`dirname ${_TMP}/${x}`"
			ecp -r ${x} ${_TMP}/${x} 
		done
	fi
}

# Copy the documentation
copy_docs()
{
        einfo "Copying documentation..."

	cd ${_TMP}

	if [ "${_USE_ZFS}" = "1" ]; then
		for x in ${_ZFS_MAN}; do
			mkdir -p "`dirname ${_TMP}/${x}`"
			ecp -r ${x} ${_TMP}/${x}
		done
	fi
}

# Copy the udev rules
copy_udev()
{
	einfo "Copying udev rules..."

	cd ${_TMP}

	if [ "${_USE_ZFS}" = "1" ]; then
		for x in ${_ZFS_UDEV}; do
			mkdir -p "`dirname ${_TMP}/${x}`"
			ecp -r ${x} ${_TMP}/${x}
		done

		# If it's an SRM, move it to the same directory that
		# sysresccd keeps their udev files.
		if [ "${_ZFS_SRM}" = "1" ]; then
			mkdir ${_TMP}/lib
			mv ${_TMP}/lib64/udev lib

			# Also do some substitions so that udev uses the correct udev_id file
			sed -i -e 's:/lib64/:/lib/:' ${_TMP}/lib/udev/rules.d/69-vdev.rules
			sed -i -e 's:/lib64/:/lib/:' ${_TMP}/lib/udev/rules.d/60-zvol.rules
		fi
	fi
}

# Gather all the dependencies (shared libraries) needed for all binaries
# Checks bin/ and sbin/ (in the tempinit after it copied the binaries
# and then copy them over.
do_deps()
{
        einfo "Getting dependencies..."

	# Add interpreter to deps since everything will depend on it
	deps="${_LIB64}/ld-linux-x86-64.so*"

	for x in ${_BASE_BINS}; do
		deps="${deps} \
		$(ldd ${x} | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}')"
	done

	if [ "${_USE_ZFS}" = "1" ]; then
		for x in ${_ZFS_BINS}; do
			deps="${deps} \
			$(ldd ${x} | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}')"
		done
	fi

	if [ "${_USE_LUKS}" = "1" ]; then
		for x in ${_LUKS_BINS}; do
			deps="${deps} \
			$(ldd ${x} | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}')"
		done
	fi

	# Eliminate duplicates
	deps=$(echo ${deps} | tr " " "\n" | sort -d | uniq)

	# Copy all the dependencies of the binary files into the initramfs
	einfo "Copying dependencies..."

	cd ${_TMP}

	for y in ${deps}; do		
                ecp --parents ${y} . 
        done
}
