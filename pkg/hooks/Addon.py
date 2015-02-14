# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the Simplified BSD License which can be found in the LICENSE file.

from pkg.hooks.Hook import Hook

class Addon(Hook):
    # A list of kernel modules to include in the initramfs
    # Format: "module1", "module2", "module3", ...
    _files = [
        # Uncomment the module below if you have encryption support built as a module, rather than built into the kernel:
        #"dm-crypt",

        # Add your modules below
        #"i915",
        #"nouveau",
    ]
