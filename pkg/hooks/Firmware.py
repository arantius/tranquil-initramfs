# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the GPLv2 which can be found in the LICENSE file.

from pkg.hooks.Hook import Hook

class Firmware(Hook):
    # Copy firmware?
    _use = 0

    # If enabled, all the firmware in /lib/firmware will be copied into the initramfs.
    # If you know exactly what firmware files you want, definitely leave this at 0 so
    # to reduce the initramfs size.
    _copy_all = 0

    # A list of firmware files to include in the initramfs
    _files = [
        # Add your firmware files below
        #"iwlwifi-6000g2a-6.ucode",
        #"/yamaha/yss225_registers.bin",
    ]

    # Gets the flag_all_firmware value
    @classmethod
    def IsCopyAllEnabled(cls):
        return cls._copy_all
