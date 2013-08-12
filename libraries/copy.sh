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
		if [[ ! -f ${x} ]]; then
			err_bin_dexi ${x}
		fi
	done

	if [[ ${USE_ZFS} == "1" ]]; then
		eflag "Using ZFS"

		for x in ${ZFS_BINS}; do	
			if [[ ! -f ${x} ]]; then
				err_bin_dexi ${x}
			fi
		done
	fi

	if [[ ${USE_LUKS} == "1" ]]; then
		eflag "Using LUKS"

		for x in ${LUKS_BINS}; do
			if [[ ! -f ${x} ]]; then
				err_bin_dexi ${x}
			fi
		done

		for x in ${GPG_BINS}; do
			if [[ ! -f ${x} ]]; then
				err_bin_dexi ${x}
			fi
		done
	fi

	if [[ ${USE_LVM} == "1" ]]; then
		eflag "Using LVM"

		for x in ${LVM_BINS}; do	
			if [[ ! -f ${x} ]]; then
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
		if [[ ${x##*/} == "busybox" ]]; then
			ecp ${x} ${T}/bin
		else
			ecp --parents ${x} ${T}
		fi
	done

	if [[ ${USE_ZFS} == "1" ]]; then
		for x in ${ZFS_BINS}; do
			ecp --parents ${x} ${T}
		done  
	fi

	if [[ ${USE_LUKS} == "1" ]]; then
		for x in ${LUKS_BINS}; do
			ecp --parents ${x} ${T}
		done

		for x in ${GPG_BINS}; do
			ecp --parents ${x} ${T}
		done
	fi

	if [[ ${USE_LVM} == "1" ]]; then
		for x in ${LVM_BINS}; do
			ecp --parents ${x} ${T}
			
			# Rename lvm.static to lvm if it exists
			if [[ -f ${LSBIN}/lvm.static ]]; then
				mv ${LSBIN}/lvm.static ${LSBIN}/lvm
			fi
		done  
	fi
}

# Get module dependencies
get_modules()
{
	einfo "Gathering module dependencies..."

	if [[ ${USE_ZFS} == "1" ]]; then
		get_moddeps "${ZFS_MODS}"
	fi

	if [[ ${USE_ADDON} == "1" ]]; then
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
	moddeps=("${moddeps[@]}" $(echo "${d[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))

	# Checks to see if the dependency list is empty.
	if [[ ${#moddeps[@]} == "0" ]] && [[ ${USE_ZFS} == "1" ]]; then
		die "Module dependencies list is empty! Something is wrong."
	fi
}

# Copy modules and dependencies to the initramfs
copy_modules()
{
        einfo "Copying modules..."

	# Making sure that the dependencies are up to date
	depmod ${KERNEL}

	if [[ ${USE_ADDON} == "1" ]] || [[ ${USE_ZFS} == "1" ]]; then
		for i in $(seq 0 $((${#moddeps[@]} - 1))); do
			ecp "--parents -r" ${moddeps[${i}]} ${T}
		done
	fi
}

# Copy the documentation
copy_docs()
{
        einfo "Copying documentation..."

	if [[ ${USE_ZFS} == "1" ]]; then
		for x in ${ZFS_MAN}; do
			mkdir -p "`dirname ${T}/${x}`"
			ecp -r ${x} ${T}/${x}
		done
	fi

	if [[ ${USE_LUKS} == "1" ]]; then
		for x in ${LUKS_MAN}; do
			mkdir -p "`dirname ${T}/${x}`"
			ecp -r ${x} ${T}/${x}
		done
	fi

	if [[ ${USE_LVM} == "1" ]]; then
		for x in ${LVM_MAN}; do
			mkdir -p "`dirname ${T}/${x}`"
			ecp -r ${x} ${T}/${x}
		done
	fi
}

# Copy the udev rules
copy_udev()
{
	einfo "Copying udev rules..."

	if [[ ${USE_ZFS} == "1" ]]; then
		for x in ${ZFS_UDEV}; do
			mkdir -p "`dirname ${T}/${x}`"
			ecp -r ${x} ${T}/${x}
		done
	fi
}

# Copy any other files that need to be copied
copy_other()
{
	einfo "Copying other files..."

	if [[ ${USE_BASE} == "1" ]]; then
		# Copy bash files
		mkdir -p ${T}/etc/bash
		cp /etc/bash/bashrc ${T}/etc/bash/
		cp /etc/DIR_COLORS ${T}/etc/
	fi

	if [[ ${USE_LUKS} == "1" ]]; then
		for x in ${GPG_FILES}; do
			ecp --parents ${x} ${T}
		done
	fi

	if [[ ${USE_LVM} == "1" ]]; then
		for x in ${LVM_FILES}; do
			ecp --parents ${x} ${T}
		done
	fi
}

# Gets dependency list for parameter
get_dlist()
{
	ldd ${1} | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}'
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
		deps="${deps} $(get_dlist ${x})"
	done

	if [[ ${USE_ZFS} == "1" ]]; then
		for x in ${ZFS_BINS}; do
			deps="${deps} $(get_dlist ${x})"
		done
	fi

	if [[ ${USE_LUKS} == "1" ]]; then
		for x in ${LUKS_BINS}; do
			deps="${deps} $(get_dlist ${x})"
		done

		for x in ${GPG_BINS}; do
			deps="${deps} $(get_dlist ${x})"
		done
	fi

	if [[ ${USE_LVM} == "1" ]]; then
		for x in ${LVM_BINS}; do
			deps="${deps} $(get_dlist ${x})"
		done
	fi

	# Eliminate duplicates
	deps=$(echo ${deps} | tr " " "\n" | sort -d | uniq)

	# Copy all the dependencies of the binary files into the initramfs
	einfo "Copying dependencies..."

	for y in ${deps}; do		
                ecp --parents ${y} ${T} 
        done
}
