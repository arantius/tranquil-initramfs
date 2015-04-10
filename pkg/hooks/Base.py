# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import pkg.libs.Variables as var

from pkg.hooks.Hook import Hook
from pkg.libs.Tools import Tools

class Base(Hook):
    @classmethod
    # Returns the kmod links
    def GetKmodLinks(cls):
        return cls._kmod_links

    _files = [
        # sys-apps/busybox
        "/bin/busybox",

        # sys-apps/kmod
        Tools.GetProgramPath("kmod"),

        # app-shells/bash
        "/bin/bash",

        # sys-apps/grep
        "/bin/egrep",
        "/bin/fgrep",
        "/bin/grep",

        # sys-apps/kbd,
        "/usr/bin/loadkeys",
    ]

    _kmod_links = [
        "depmod",
        "insmod",
        "lsmod",
        "modinfo",
        "modprobe",
        "rmmod",
    ]
