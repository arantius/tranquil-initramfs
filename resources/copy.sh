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
	for x in ${BASE_BINS}; do
		if [ ! -f "${x}" ]; then
			err_bin_dexi ${x}
		fi
	done

	if [ "${USE_ZFS}" = "1" ]; then
		eflag "Using ZFS"

		for x in ${INIT_BINS}; do	
			if [ ! -f "${x}" ]; then
				err_bin_dexi ${x}
			fi
		done
	fi

	if [ "${USE_LUKS}" = "1" ]; then
		eflag "Using LUKS"

		for x in ${LUKS_BINS}; do
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

	if [ "${USE_ZFS}" = "1" ]; then
		for x in ${ZFS_MODS}; do
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
	for x in ${BASE_BINS}; do
		ecp ${x} ${TMP_CORE}/${x}
	done

	if [ "${USE_ZFS}" = "1" ]; then
		for x in ${ZFS_BINS}; do
			ecp ${x} ${TMP_CORE}/${x}
		done  
	fi

	if [ "${USE_LUKS}" = "1" ]; then
		for x in ${LUKS_BINS}; do
			ecp ${x} ${TMP_CORE}/${x}
		done
	fi
}

# Copy the required modules to the initramfs
copy_modules()
{
        einfo "Copying modules..."

	if [ "${ZFS_SRM}" = "1" ]; then
		for x in ${ZFS_MODS}; do 
			mkdir -p "`dirname ${TMP_KMOD}/${x}`"
			ecp -r ${x} ${TMP_KMOD}/${x} 
		done
	elif [ "${USE_ZFS}" = "1" ]; then
		for x in ${ZFS_MODS}; do 
			mkdir -p "`dirname ${TMP_CORE}/${x}`"
			ecp -r ${x} ${TMP_CORE}/${x} 
		done
	fi
}

# Copy the documentation
copy_docs()
{
        einfo "Copying documentation..."

	if [ "${USE_ZFS}" = "1" ]; then
		for x in ${ZFS_MAN}; do
			mkdir -p "`dirname ${TMP_CORE}/${x}`"
			ecp -r ${x} ${TMP_CORE}/${x}
		done
	fi
}

# Copy the udev rules
copy_udev()
{
	einfo "Copying udev rules..."

	if [ "${USE_ZFS}" = "1" ]; then
		for x in ${ZFS_UDEV}; do
			mkdir -p "`dirname ${TMP_CORE}/${x}`"
			ecp -r ${x} ${TMP_CORE}/${x}
		done

		# If it's a SB, move it to the same directory that
		# SLAX keeps its udev files.
		if [ "${ZFS_SRM}" = "1" ]; then
			mkdir ${TMP_CORE}/lib
			mv ${TMP_CORE}/lib64/udev ${TMP_CORE}/lib

			# Also do some substitions so that udev uses the correct udev_id file
			sed -i -e 's:/lib64/:/lib/:' ${TMP_CORE}/lib/udev/rules.d/69-vdev.rules
			sed -i -e 's:/lib64/:/lib/:' ${TMP_CORE}/lib/udev/rules.d/60-zvol.rules
		fi
	fi
}

# Copy any other files that need to be copied
copy_other()
{
	einfo "Copying other files..."

	# Copy Bash Files
	for x in ${BASH_FILES}; do
		ecp --parents ${x} ${TMP_CORE}
	done

	# Modify Bash Stuff
	#sed -i -e '63s%\[\033[01;31m\]\h%ok%' ${LOCAL_ETC}/bash/bashrc
	#sed -i -e '9d' ${LOCAL_ETC}/bash/bashrc

	# Copy Vim Files
	for x in ${VIM_FILES}; do
		ecp --parents ${x} ${TMP_CORE}
	done
}
# Gather all the dependencies (shared libraries) needed for all binaries
# Checks bin/ and sbin/ (in the tempinit after it copied the binaries
# and then copy them over.
do_deps()
{
        einfo "Getting dependencies..."

	# Add interpreter to deps since everything will depend on it
	deps="${LIB64}/ld-linux-x86-64.so*"

	for x in ${BASE_BINS}; do
		deps="${deps} \
		$(ldd ${x} | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}')"
	done

	if [ "${USE_ZFS}" = "1" ]; then
		for x in ${ZFS_BINS}; do
			deps="${deps} \
			$(ldd ${x} | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}')"
		done
	fi

	if [ "${USE_LUKS}" = "1" ]; then
		for x in ${LUKS_BINS}; do
			deps="${deps} \
			$(ldd ${x} | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}')"
		done
	fi

	# Eliminate duplicates
	deps=$(echo ${deps} | tr " " "\n" | sort -d | uniq)

	# Copy all the dependencies of the binary files into the initramfs
	einfo "Copying dependencies..."

	for y in ${deps}; do		
                ecp --parents ${y} ${TMP_CORE} 
        done
}
