# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
