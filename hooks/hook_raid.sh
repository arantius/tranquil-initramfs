# Copyright (C) 2012 Jonathan Vasquez
#
# Distributed under the GPLv2 which can be found in the LICENSE file.

# Source RAID specific functions
. resources/functions_raid.sh

# Required Binaries, Modules, and other files
JV_INIT_BINS="busybox hostid mdadm"

# Set init type
INIT_TYPE="RAID"

# Init file in files/
INIT_FILE="init_raid"

# Ask for desired kernel
eline && get_target_kernel
