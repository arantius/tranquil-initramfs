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

	if [ "${USE_ZFS}" == "1" ]; then
		eflag "Using ZFS"

		for x in ${INIT_BINS}; do	
			if [ ! -f "${x}" ]; then
				err_bin_dexi ${x}
			fi
		done
	fi

	if [ "${USE_LUKS}" == "1" ]; then
		eflag "Using LUKS"

		for x in ${LUKS_BINS}; do
			if [ ! -f "${x}" ]; then
				err_bin_dexi ${x}
			fi
		done

		for x in ${GPG_BINS}; do
			if [ ! -f "${x}" ]; then
				err_bin_dexi ${x}
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
		ecp --parents ${x} ${TMP_CORE}
	done

	if [ "${USE_ZFS}" == "1" ]; then
		for x in ${ZFS_BINS}; do
			ecp --parents ${x} ${TMP_CORE}
		done  
	fi

	if [ "${USE_LUKS}" == "1" ]; then
		for x in ${LUKS_BINS}; do
			ecp --parents ${x} ${TMP_CORE}
		done

		for x in ${GPG_BINS}; do
			ecp --parents ${x} ${TMP_CORE}
		done
	fi
}

# Get module dependencies
get_modules()
{
	einfo "Gathering module dependencies..."

	if [ "${USE_ADDON}" == "1" ]; then
		get_moddeps "${ADDON_MODS}"
	fi
}

# Gets the dependencies for only one module
get_moddeps()
{
	for i in ${@}; do
		# Concatenate the previous results with the current ones
		local d=("${d[@]}" $(modprobe -S ${KERNEL} --show-depends ${i} | awk -F ' ' '{print $2}'))
	done

	# Remove Duplicates
	moddeps=($(echo "${d[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))
}

# Copy modules and dependencies to the initramfs
copy_modules()
{
        einfo "Copying modules..."

	if [ "${USE_ADDON}" == "1" ]; then
		for i in $(seq 0 $((${#moddeps[@]} - 1))); do
			ecp "--parents -r" ${moddeps[${i}]} ${TMP_CORE}
		done
	fi

	if [ "${ZFS_SRM}" == "1" ]; then
		get_moddeps zfs

		for i in $(seq 0 $((${#moddeps[@]} - 1))); do
			ecp "--parents -r" ${moddeps[${i}]} ${TMP_KMOD}
		done
	fi
}

# Copy the documentation
copy_docs()
{
        einfo "Copying documentation..."

	if [ "${USE_ZFS}" == "1" ]; then
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

	if [ "${USE_ZFS}" == "1" ]; then
		for x in ${ZFS_UDEV}; do
			mkdir -p "`dirname ${TMP_CORE}/${x}`"
			ecp -r ${x} ${TMP_CORE}/${x}
		done

		# If it's a SB, move it to the same directory that
		# SLAX keeps its udev files.
		if [ "${ZFS_SRM}" == "1" ]; then
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

	if [ "${USE_BASE}" == "1" ]; then
		# Copy Bash Files
		for x in ${BASH_FILES}; do
			ecp --parents ${x} ${TMP_CORE}
		done

		# Modify Bash Stuff

		# This fixes the (no host) crap that will be shown when you go into rescue shell
		sed -i -e '63d' ${LOCAL_ETC}/bash/bashrc
		sed -i -e "62a \\\t\tPS1='\\\[\\\033[01;31m\\\]initrd\\\[\\\033[01;34m\\\] \\\\W \\\\$\\\[\\\033[00m\\\] '" ${LOCAL_ETC}/bash/bashrc
		sed -i -e '73d' ${LOCAL_ETC}/bash/bashrc
		sed -i -e "72a \\\t\tPS1='\\\u@initrd \\\W \\\\$ '" ${LOCAL_ETC}/bash/bashrc
		sed -i -e '75d' ${LOCAL_ETC}/bash/bashrc
		sed -i -e "74a \\\t\tPS1='\\\u@initrd \\\w \\\\$ '" ${LOCAL_ETC}/bash/bashrc

		# Copy Vim Files
		for x in ${VIM_FILES}; do
			ecp "--parents -r" ${x} ${TMP_CORE}
		done

		# Copy other files
		for x in ${OTHER_FILES}; do
			ecp "--parents -r" ${x} ${TMP_CORE}
		done
	fi

	if [ "${USE_LUKS}" == "1" ]; then
		for x in ${GPG_FILES}; do
			ecp --parents ${x} ${TMP_CORE}
		done
	fi

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

		for x in ${GPG_BINS}; do
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

