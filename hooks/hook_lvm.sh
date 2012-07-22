# Copyright (C) 2012 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# Distributed under the ISC license which can be found in the LICENSE file.

# Source LVM Specific Functions
. resources/functions_lvm.sh

# Required Binaries, Modules, and other files
JV_INIT_BINS="busybox hostid lvm.static"

# Set init type
INIT_TYPE="LVM"

# Init file in files/
INIT_FILE="init_lvm"

# Ask for desired kernel if one wasn't passed
eline && get_target_kernel
