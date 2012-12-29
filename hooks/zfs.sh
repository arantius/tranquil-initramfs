# Copyright (C) 2012 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Source ZFS Specific Functions
. resources/zfs.sh

# Required Binaries, Modules, and other files
JV_INIT_BINS="busybox zpool_layout hostid spl splat mount.zfs zdb zfs zinject zpios zpool zstreamdump ztest"
JV_INIT_MODS="spl splat zavl znvpair zunicode zcommon zfs zpios"

# Set init type
INIT_TYPE="ZFS"

# Init file in files/
INIT_FILE="zfs"

# Ask for desired kernel
eline && get_target_kernel

# Set the modules path for this kernel
set_target_kernel
