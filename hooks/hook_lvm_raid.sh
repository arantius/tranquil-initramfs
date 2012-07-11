# Copyright (C) 2012 Jonathan Vasquez
#
# Distributed under the MIT license which can be found in the LICENSE file.

# Source LVM/RAID Specific Functions
. resources/functions_lvm_raid.sh

# Required Binaries, Modules, and other files
JV_INIT_BINS="busybox hostid lvm.static mdadm"

# Set init type
INIT_TYPE="LVM-RAID"

# Init file in files/
INIT_FILE="init_lvm_raid"

# Ask for desired kernel
eline && get_target_kernel
