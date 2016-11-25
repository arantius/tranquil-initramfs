# Copyright 2012-2016 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

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
        "/usr/share/gnupg/gpg-conf.skel",

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
