# Copyright (C) 2012 Jonathan Vasquez
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
