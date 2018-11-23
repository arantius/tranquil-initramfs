# Copyright (C) 2012-2018 Jonathan Vasquez <jon@xyinn.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see<https://www.gnu.org/licenses/>.

from pkg.hooks.Hook import Hook

class Luks(Hook):
    # Should we embed our keyfile into the initramfs?
    _use_keyfile = 0

    # Path to the keyfile you would like to embedded directly into the initramfs.
    # This should be a non-encrypted keyfile since it will be used to automate
    # the decryption of your / pool (when your /boot is also on /).
    _keyfile_path = "/crypto_keyfile.bin"

    # Should we embed our LUKS header into the initramfs?
    _use_detached_header = 0

    # Path to the LUKS header you would like to embedded directly into the initramfs.
    _detached_header_path = "/crypto_header.bin"

    # Required Files
    _files = [
        "/sbin/cryptsetup",
        "/usr/bin/gpg",
        "/usr/bin/gpg-agent",

        # Used for udev cookie release when cryptsetup announces udev support
        # and attempts to decrypt the drive. Without this, the cryptsetup will lock up
        # and stay at "waiting for zero"
        "/sbin/dmsetup",
    ]

    # Is embedding the keyfile enabled?
    @classmethod
    def IsKeyfileEnabled(cls):
        return cls._use_keyfile

    # Return the keyfile path
    @classmethod
    def GetKeyfilePath(cls):
        return cls._keyfile_path

    # Is embedding the LUKS header enabled?
    @classmethod
    def IsDetachedHeaderEnabled(cls):
        return cls._use_detached_header

    # Return the LUKS header path
    @classmethod
    def GetDetachedHeaderPath(cls):
        return cls._detached_header_path
