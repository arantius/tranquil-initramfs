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

# Application Info
_NAME="Bliss Initramfs Creator"
_AUTHOR="Jonathan Vasquez"
_EMAIL="jvasquez1011@gmail.com"
_CONTACT="${_AUTHOR} <${_EMAIL}>"
_VERSION="1.8.0"
_LICENSE="Simplified BSD License"

# Used only for documentation purposes
_EXAMPLE_KERNEL="3.8.13-ALL"

# Parameters and Locations
_KERNEL=""
_INITRD=""
_INIT=""

_HOME="$(pwd)"
_TMP_CORE="${_HOME}/temp_core"
_TMP_KMOD="${_HOME}/temp_kmod"

_BIN="/bin"
_SBIN="/sbin"
_LIB="/lib"
_LIB64="/lib64"
_MAN="/usr/share/man"
_UDEV="${_LIB64}/udev"

_LOCAL_BIN="${_TMP_CORE}/${_BIN}"
_LOCAL_SBIN="${_TMP_CORE}/${_SBIN}"
_LOCAL_LIB="${_TMP_CORE}/${_LIB}"
_LOCAL_LIB64="${_TMP_CORE}/${_LIB64}"
_LOCAL_MAN="${_TMP_CORE}/${_MAN}"
_LOCAL_UDEV="${_TMP_CORE}/${_UDEV}"

_USR_BIN="/usr/bin"
_USR_SBIN="/usr/sbin"
_USR_LIB="/usr/lib"

_MODULES=""        # will be set by the `setTargetKernel` function
_LOCAL_MODULES=""  # will be set by the `setTargetKernel` function

# Get CPU Architecture
_ARCH="$(uname -m)"

# Basically a boolean that is used to switch to the correct library path
_LIB_PATH=""

# Required Busybox Symlinks
_BUSYBOX_LN="mount tty sh"

# Preliminary binaries needed for the success of creating the initrd
# but that are not needed to be placed inside the initrd
_PREL_BIN="/bin/cpio"

# Directories to create when generating the initramfs structure
_CDIRS="${_TMP_CORE}/bin \
	${_TMP_CORE}/sbin \
	${_TMP_CORE}/usr/bin \
        ${_TMP_CORE}/proc \
	${_TMP_CORE}/sys \
	${_TMP_CORE}/dev \
	${_TMP_CORE}/etc \
	${_TMP_CORE}/mnt/root \
	${_TMP_CORE}/resources \
	${_TMP_CORE}/lib"

# zpool.cache
_ZCACHE="/etc/zfs/zpool.cache"
