#!/usr/bin/env python

# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from ..libs.variables import *

# Enable/Disable Hook
use_base = "0"

# Required Packages
base_packs = [
    "sys-apps/baselayout",
    "sys-apps/busybox",
    "sys-apps/coreutils",
    "sys-apps/grep",
    "sys-apps/kmod",
    "app-shells/bash",
    "sys-apps/util-linux",

    # Full man pages support
    #"sys-apps/openrc",
    #"app-misc/editor-wrapper",
    #"sys-apps/less",
    #"sys-apps/groff",
    #"sys-apps/man-db",
    #"sys-libs/glibc",
    #"sys-libs/ncurses"
]
