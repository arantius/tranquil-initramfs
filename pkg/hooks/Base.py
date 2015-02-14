# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the Simplified BSD License which can be found in the LICENSE file.

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
        "/etc/bash/bashrc",
        "/etc/DIR_COLORS",
        "/etc/profile",

        # sys-apps/grep
        "/bin/egrep",
        "/bin/fgrep",
        "/bin/grep",
    ]

    _kmod_links = [
        "depmod",
        "insmod",
        "lsmod",
        "modinfo",
        "modprobe",
        "rmmod",
    ]
