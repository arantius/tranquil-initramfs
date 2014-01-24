#!/usr/bin/env python

# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from ..libs.variables import *

# Enable/Disable Hook
use_zfs = "0"

# Required Packages
zfs_packs = [
        "sys-kernel/spl"
        "sys-fs/zfs"
        "sys-fs/zfs-kmod"
]
