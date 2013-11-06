#!/usr/bin/env python

# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from ..libs.variables import *

# Enable/Disable Hook
use_zfs = "0"

# Required Binaries, Modules, and other files
zfs_bins = [
        ubin + "/hostid",
        sbin + "/fsck.zfs",
        sbin + "/mount.zfs",
        sbin + "/zdb",
        sbin + "/zfs",
        sbin + "/zhack",
        sbin + "/zinject",
        sbin + "/zpios",
        sbin + "/zpool",
        sbin + "/zstreamdump",
        sbin + "/ztest"]

zfs_man = [
        man + "/man1/zhack.1.*",
        man + "/man1/zpios.1.*",
        man + "/man1/ztest.1.*",
        man + "/man5/vdev_id.conf.5.*",
        man + "/man5/zpool-features.5.*",
        man + "/man8/fsck.zfs.8.*",
        man + "/man8/mount.zfs.8.*",
        man + "/man8/vdev_id.8.*",
        man + "/man8/zdb.8.*",
        man + "/man8/zfs.8.*",
        man + "/man8/zinject.8.*",
        man + "/man8/zpool.8.*",
        man + "/man8/zstreamdump.8.*"]

# Currently not being used
zfs_udev = [
        udev + "/rules.d/60-zvol.rules",
        udev + "/rules.d/69-vdev.rules",
        udev + "/rules.d/90-zfs.rules",
        udev + "/vdev_id",
        udev + "/zvol_id"]
