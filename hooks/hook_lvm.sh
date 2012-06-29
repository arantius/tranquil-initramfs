# Copyright (C) 2012 Jonathan Vasquez
#
# This source code is released under the MIT license which can be found
# in the LICENSE file.

# Source LVM Specific Functions
. resources/functions_lvm.sh

# Required Binaries, Modules, and other files
JV_INIT_BINS="busybox hostid lvm"

# Set init type
INIT_TYPE="LVM"

# Init file in files/
INIT_FILE="init_lvm"

# Ask for desired kernel
eline && get_target_kernel
