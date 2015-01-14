# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>.

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
