# Copyright (C) 2012-2020 Jonathan Vasquez <jon@xyinn.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pkg.hooks.Hook import Hook


class Zfs(Hook):
    # Should we copy the man pages?
    _use_man = 0

    # Required Files
    _files = ["/sbin/fsck.zfs", "/sbin/mount.zfs", "/sbin/zfs", "/sbin/zpool"]

    # Optional Files. Will not fail if we fail to copy them.
    _optional_files = [
        "/sbin/zdb",
        "/sbin/zhack",
        "/sbin/zinject",
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

    @classmethod
    def LoadConfig(cls, config):
      cls._use_man = config['Zfs'].getboolean('use_man', False)
