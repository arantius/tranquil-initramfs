# Copyright (C) 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Toggle Flags
USE_LVM="1"

# Set the kernel we will be using here
do_kernel

# Required Binaries, Modules, and other files
if [[ -f "${SBIN}/lvm.static" ]]; then
	LVM_BINS="${SBIN}/lvm.static"
else
	LVM_BINS="${SBIN}/lvm"
fi

LVM_MAN="${MAN}/man8/lvm.8.*"

LVM_FILES="/etc/lvm/lvm.conf"
