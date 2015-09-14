# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

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

    # TODO: Portage allows on to change the compression type with PORTAGE_COMPRESS.
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
