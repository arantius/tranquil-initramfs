# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the Simplified BSD License which can be found in the LICENSE file.

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
    ]
