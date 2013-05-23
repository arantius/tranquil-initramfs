# Simplified BSD License
#
# Copyright (C) 2013 Jonathan Vasquez <jvasquez1011@gmail.com> 
# All Rights Reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
			local p=$(dirname ${TMP_KMOD}/${x} | sed 's:/lib/:/lib64/:')
			mkdir -p ${p} && ecp -r ${x} ${p} 
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

		# If it's an SRM, move it to the same directory that
		# sysresccd keeps their udev files.
		if [ "${ZFS_SRM}" = "1" ]; then
			mkdir ${TMP_CORE}/lib
			mv ${TMP_CORE}/lib64/udev ${TMP_CORE}/lib

			# Also do some substitions so that udev uses the correct udev_id file
			sed -i -e 's:/lib64/:/lib/:' ${TMP_CORE}/lib/udev/rules.d/69-vdev.rules
			sed -i -e 's:/lib64/:/lib/:' ${TMP_CORE}/lib/udev/rules.d/60-zvol.rules
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
