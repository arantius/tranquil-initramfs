# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the Simplified BSD License which can be found in the LICENSE file.

from pkg.hooks.Hook import Hook

class Zfs(Hook):
    # Required Files
    _files = [
        "/sbin/mount.zfs",
        "/sbin/zdb",
        "/sbin/zfs",
        "/sbin/zpool",
    ]
