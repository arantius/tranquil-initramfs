# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# This Source Code Form is "Incompatible With Secondary Licenses", as
# defined by the Mozilla Public License, v. 2.0.

# Application Info
_NAME="Bliss Initramfs Creator"
_AUTHOR="Jonathan Vasquez"
_EMAIL="jvasquez1011@gmail.com"
_CONTACT="${_AUTHOR} <${_EMAIL}>"
_VERSION="1.6.4"
_LICENSE="MPLv2"

# Used only for documentation purposes
_EXAMPLE_KERNEL="3.7.2-ALL"

# Parameters and Locations
_KERNEL=""
_INITRD=""
_INIT=""

_HOME="$(pwd)"
_TMP="${_HOME}/tempinit/"

_BIN="/bin/"
_SBIN="/sbin/"
_LIB="/lib/"
_LIB64="/lib64/"
_MAN="/usr/share/man/"
_UDEV="${_LIB64}/udev" # Not used

_LOCAL_BIN="${_TMP}/${_BIN}"
_LOCAL_SBIN="${_TMP}/${_SBIN}"
_LOCAL_LIB="${_TMP}/${_LIB}"
_LOCAL_LIB64="${_TMP}/${_LIB64}"
_LOCAL_MAN="${_TMP}/${_MAN}"
_LOCAL_UDEV="${_TMP}/${_UDEV}"

_USR_BIN="/usr/bin/"
_USR_SBIN="/usr/sbin/"
_USR_LIB="/usr/lib/"

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
_PREL_BIN="/bin/cpio \
	   /usr/bin/mksquashfs"

# Directories to create when generating the initramfs structure
_CDIRS="bin \
	sbin \
	usr/bin \
        proc \
	sys \
	dev \
	etc \
	mnt/root \
	resources \
	lib"

# zpool.cache
_ZCACHE="/etc/zfs/zpool.cache"
