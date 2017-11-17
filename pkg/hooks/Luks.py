# Copyright 2012-2017 Jonathan Vasquez <jon@xyinn.org>
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
