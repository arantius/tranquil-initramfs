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

class Udev(Hook):
    # Enable udev support?
    _use = 1

    # Required Files
    _files = [
        # udev
        Tools.GetUdevPath(),
        Tools.GetProgramPath("udevadm"),

        # Used for udev cookie release when cryptsetup announces udev support
        # and attempts to decrypt the drive. Without this, the cryptsetup will lock up
        # and stay at "waiting for zero"
        "/sbin/dmsetup",
    ]
