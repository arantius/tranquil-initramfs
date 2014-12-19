# Copyright 2012-2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pkg.hooks.hook import Hook

class Addon(Hook):
    def __init__(self):
        Hook.__init__(self)

        # A list of kernel modules to include in the initramfs
        # Format: "module1", "module2", "module3", ...
        self.files = [
            # Uncomment the module below if you have encryption support built as a module, rather than built into the kernel:
            #"dm-crypt",

            # Add your modules below
            #"",
        ]
