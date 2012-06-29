# Copyright (C) 2012 Jonathan Vasquez
#
# This source code is released under the MIT license which can be found
# in the LICENSE file.

# Application Info
JV_APP_NAME="Bliss Initramfs Creator"
JV_AUTHOR="Jonathan Vasquez"
JV_EMAIL="jvasquez1011@gmail.com"
JV_CONTACT="${JV_AUTHOR} <${JV_EMAIL}>"
JV_VERSION="1.4.2"
JV_LICENSE="MIT"
JV_DISTRO="Funtoo Linux"

# Used only for documentation purposes
JV_EXAMPLE_KERNEL="3.4.4-DESKTOP"

# Parameters and Locations
KERNEL_NAME=""

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

# Variables listed here will be defined in another place
MOD_PATH="" # will be set by the `getTargetKernel` function
JV_LOCAL_MOD="" # will be set by the `getTargetKernel` function

# Get CPU Architecture
JV_CARCH="$(uname -m)"

# Basically a boolean that is used to switch to the correct library path
# Defaults to 32 bit
JV_LIB_PATH=32

# Required Binaries, Modules, and other files
BUSYBOX_TARGETS="mount tty sh"
