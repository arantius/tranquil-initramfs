# Copyright 2012-2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pkg.hooks.hook import Hook
from pkg.libs.toolkit import Toolkit as tools

class Base(Hook):
    def __init__(self):
        Hook.__init__(self)

        # Activate the Base implicitly since it will always be included in all initramfs
        self.use = 1

        # Set the kmod path for this system
        self.kmod_path = tools.find_prog("kmod")

        self.udev_path = tools.find_udevd()
        self.udevadm_path = tools.find_prog("udevadm")

        self.files = [
            # sys-apps/busybox
            "/bin/busybox",

            # sys-apps/kmod
            self.kmod_path,

            # udev
            self.udev_path,
            self.udevadm_path,

            # used for udev cookie release when cryptsetup announces udev support
            # and attempts to decrypt the drive. Without this, the cryptsetup will lock up
            # and stay at "waiting for zero"
            "/sbin/dmsetup",

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

        self.kmod_links = [
            "depmod",
            "insmod",
            "lsmod",
            "modinfo",
            "modprobe",
            "rmmod",
        ]

    # Returns the kmod path
    def get_kmod_path(self):
        return self.kmod_path

    # Returns the kmod links
    def get_kmod_links(self):
        return self.kmod_links
