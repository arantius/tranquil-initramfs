# Copyright (C) 2012 Jonathan Vasquez
#
# This source code is released under the MIT license which can be found
# in the LICENSE file.

# Source LVM Specific Functions
. resources/functions_lvm_raid.sh

# Required Binaries, Modules, and other files
JV_INIT_BINS="busybox hostid lvm mdadm"

# Set init type
INIT_TYPE="LVM_RAID"

# Init file in files/
INIT_FILE="init_lvm_raid"

# Ask for desired kernel
eline && get_target_kernel
