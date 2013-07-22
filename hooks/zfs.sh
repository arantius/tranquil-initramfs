# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Toggle Flags
USE_ZFS="1"

# Set the kernel we will be using here
do_kernel

# Required Binaries, Modules, and other files
ZFS_BINS="
	${UBIN}/hostid
	${SBIN}/fsck.zfs
	${SBIN}/mount.zfs
	${SBIN}/zdb
	${SBIN}/zfs
	${SBIN}/zhack
	${SBIN}/zinject
	${SBIN}/zpios
	${SBIN}/zpool
	${SBIN}/zstreamdump
	${SBIN}/ztest"

ZFS_MAN="
	${MAN}/man1/zhack.1.bz2
	${MAN}/man1/zpios.1.bz2
	${MAN}/man1/ztest.1.bz2
	${MAN}/man5/vdev_id.conf.5.bz2
	${MAN}/man5/zpool-features.5.bz2
	${MAN}/man8/fsck.zfs.8.bz2
	${MAN}/man8/mount.zfs.8.bz2
	${MAN}/man8/vdev_id.8.bz2
	${MAN}/man8/zdb.8.bz2
	${MAN}/man8/zfs.8.bz2
	${MAN}/man8/zinject.8.bz2
	${MAN}/man8/zpool.8.bz2
	${MAN}/man8/zstreamdump.8.bz2"

ZFS_UDEV="
	${UDEV}/rules.d/60-zvol.rules
	${UDEV}/rules.d/69-vdev.rules
	${UDEV}/rules.d/90-zfs.rules
	${UDEV}/vdev_id
	${UDEV}/zvol_id"
