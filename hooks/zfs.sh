# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Toggle Flags
_USE_ZFS="1"
_USE_MODULES="1"

# Required Binaries, Modules, and other files
_ZFS_BINS="zpool_layout hostid spl splat mount.zfs zdb zfs zinject zpios zpool zstreamdump ztest"
_ZFS_MODS="spl splat zavl znvpair zunicode zcommon zfs zpios"

_ZFS_MAN5="vdev_id.conf.5.bz2"

_ZFS_MAN8="vdev_id.8.bz2 \
	   zdb.8.bz2 \
	   zfs.8.bz2 \
	   zpool.8.bz2 \
	   zstreamdump.8.bz2"
