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
NAME="Bliss Initramfs Creator"
AUTHOR="Jonathan Vasquez"
EMAIL="jvasquez1011@gmail.com"
CONTACT="${AUTHOR} <${EMAIL}>"
VERSION="1.8.1"
LICENSE="Simplified BSD License"

# Used only for documentation purposes
EXAMPLE_KERNEL="3.8.13-ALL"

# Parameters and Locations
KERNEL=""
INITRD=""
INIT=""

HOME="$(pwd)"
TMP_CORE="${HOME}/temp_core"
TMP_KMOD="${HOME}/temp_kmod"

BIN="/bin"
SBIN="/sbin"
LIB="/lib"
LIB64="/lib64"
MAN="/usr/share/man"
UDEV="${LIB64}/udev"

LOCAL_BIN="${TMP_CORE}/${BIN}"
LOCAL_SBIN="${TMP_CORE}/${SBIN}"
LOCAL_LIB="${TMP_CORE}/${LIB}"
LOCAL_LIB64="${TMP_CORE}/${LIB64}"
LOCAL_MAN="${TMP_CORE}/${MAN}"
LOCAL_UDEV="${TMP_CORE}/${UDEV}"

USR_BIN="/usr/bin"
USR_SBIN="/usr/sbin"
USR_LIB="/usr/lib"

MODULES=""        # will be set by the `setTargetKernel` function
LOCAL_MODULES=""  # will be set by the `setTargetKernel` function

# Get CPU Architecture
ARCH="$(uname -m)"

# Basically a boolean that is used to switch to the correct library path
LIB_PATH=""

# Required Busybox Symlinks
BUSYBOX_LN="mount tty sh"

# Preliminary binaries needed for the success of creating the initrd
# but that are not needed to be placed inside the initrd
PREL_BIN="/bin/cpio"

# Directories to create when generating the initramfs structure
CDIRS="${TMP_CORE}/bin \
	${TMP_CORE}/sbin \
	${TMP_CORE}/usr/bin \
        ${TMP_CORE}/proc \
	${TMP_CORE}/sys \
	${TMP_CORE}/dev \
	${TMP_CORE}/etc \
	${TMP_CORE}/mnt/root \
	${TMP_CORE}/resources \
	${TMP_CORE}/lib"

# zpool.cache
ZCACHE="/etc/zfs/zpool.cache"
