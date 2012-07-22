# Copyright (C) 2012 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# Distributed under the ISC license which can be found in the LICENSE file.

# Source LVM Specific Functions
. resources/functions_zfs.sh

# Required Binaries, Modules, and other files
JV_INIT_BINS="busybox zpool_layout hostid spl splat mount.zfs zdb zfs zinject zpios zpool ztest"
JV_INIT_MODS="spl splat zavl znvpair zunicode zcommon zfs zpios"

# Set init type
INIT_TYPE="ZFS"

# Init file in files/
INIT_FILE="init_zfs"

# Ask for desired kernel
eline && get_target_kernel

# Set the modules path for this kernel
set_target_kernel
