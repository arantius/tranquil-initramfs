# Copyright (C) 2012 Jonathan Vasquez
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Source LVM Specific Functions
. resources/functions_lvm.sh

# Required Binaries, Modules, and other files
JV_INIT_BINS="busybox hostid lvm"
JV_INIT_MODS=""

# Init file in files/
INIT_FILE="init_lvm"

# Ask for desired kernel
getTargetKernel	

# Ask for lvm pool and root name
echo -n "Please enter LVM pool name: " && read LVM_POOL_NAME

echo -n "Please enter LVM root name: " && read LVM_ROOT_NAME
