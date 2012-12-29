# Copyright (C) 2012 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Application Info
JV_APP_NAME="Bliss Initramfs Creator"
JV_AUTHOR="Jonathan Vasquez"
JV_EMAIL="jvasquez1011@gmail.com"
JV_CONTACT="${JV_AUTHOR} <${JV_EMAIL}>"
JV_VERSION="1.5.1"
JV_LICENSE="MPLv2"

# Used only for documentation purposes
JV_EXAMPLE_KERNEL="3.7.1-ALL"

# Parameters and Locations
KERNEL_NAME=""
INITRD_NAME=""
MOD_PATH="" # will be set by the `getTargetKernel` function
JV_LOCAL_MOD="" # will be set by the `getTargetKernel` function

HOME_DIR="$(pwd)"
TMPDIR="${HOME_DIR}/tempinit/"

JV_LOCAL_BIN="bin/"
JV_LOCAL_SBIN="sbin/"
JV_LOCAL_LIB="lib/"
JV_LOCAL_LIB64="lib64/"
JV_BIN="/bin/"
JV_SBIN="/sbin/"
JV_LIB32="/lib/"
JV_LIB64="/lib64/"
JV_USR_LIB="/usr/lib/"
JV_USR_BIN="/usr/bin/"
JV_USR_SBIN="/usr/sbin/"

# Get CPU Architecture
JV_CARCH="$(uname -m)"

# Basically a boolean that is used to switch to the correct library path
# Defaults to 32 bit
JV_LIB_PATH=32

# Required Binaries, Modules, and other files
BUSYBOX_TARGETS="mount tty sh"

# Preliminary binaries needed for the success of creating the initrd
# but that are not needed to be placed inside the initrd
JV_PREL_BINS="cpio"
