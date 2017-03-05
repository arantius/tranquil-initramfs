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

class Zfs(Hook):
    # Should we copy the man pages?
    _use_man = 0

    # Required Files
    _files = [
        "/sbin/fsck.zfs",
        "/sbin/mount.zfs",
        "/sbin/zdb",
        "/sbin/zfs",
        "/sbin/zpool",
    ]

    # Optional Files. Will not fail if we fail to copy them.
    _optional_files = [
        "/sbin/zhack",
        "/sbin/zinject",
        "/sbin/zpios",
        "/sbin/zstreamdump",
        "/sbin/ztest",
    ]

    # Man Pages. Not used for actual initramfs environment
    # since the initramfs doesn't have the applications required to
    # display these man pages without increasing the size a lot. However,
    # these are used by the 'sysresccd-moddat' scripts to generate
    # the sysresccd + zfs isos.

    # TODO: Portage allows one to change the compression type with PORTAGE_COMPRESS.
    # In this situation, these files will have a different extension.
    # We should add a function to return the file with the correct extension.
    _man = [
        "/usr/share/man/man5/spl-module-parameters.5.bz2",
        "/usr/share/man/man1/zhack.1.bz2",
        "/usr/share/man/man1/zpios.1.bz2",
        "/usr/share/man/man1/ztest.1.bz2",
        "/usr/share/man/man5/vdev_id.conf.5.bz2",
        "/usr/share/man/man5/zfs-events.5.bz2",
        "/usr/share/man/man5/zfs-module-parameters.5.bz2",
        "/usr/share/man/man5/zpool-features.5.bz2",
        "/usr/share/man/man8/fsck.zfs.8.bz2",
        "/usr/share/man/man8/mount.zfs.8.bz2",
        "/usr/share/man/man8/vdev_id.8.bz2",
        "/usr/share/man/man8/zdb.8.bz2",
        "/usr/share/man/man8/zfs.8.bz2",
        "/usr/share/man/man8/zinject.8.bz2",
        "/usr/share/man/man8/zpool.8.bz2",
        "/usr/share/man/man8/zstreamdump.8.bz2",
    ]
