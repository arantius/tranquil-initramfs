# Copyright (C) 2012-2019 Jonathan Vasquez <jon@xyinn.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

        # udev
        Tools.GetUdevPath(),
        Tools.GetProgramPath("udevadm"),
    ]

    _kmod_links = [
        "depmod",
        "insmod",
        "lsmod",
        "modinfo",
        "modprobe",
        "rmmod",
    ]
