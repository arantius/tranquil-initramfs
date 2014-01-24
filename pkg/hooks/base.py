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
    "sys-libs/glibc",
    "app-misc/editor-wrapper",
    "sys-libs/ncurses",
    "sys-apps/less",
    "sys-apps/util-linux",
    "sys-apps/kmod",
    "sys-apps/openrc",
    "app-shells/bash",
    "sys-apps/groff",
    "sys-apps/man-db"
]

# Names of module related applications that will replace the busybox ones
kmod_sym = [
	"depmod",
	"insmod",
	"lsmod",
	"modinfo",
	"modprobe",
	"rmmod"
]
