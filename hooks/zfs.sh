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
	$(whereis hostid | cut -d " " -f 2)
	$(whereis fsck.zfs | cut -d " " -f 2)
	$(whereis mount.zfs | cut -d " " -f 2)
	$(whereis zdb | cut -d " " -f 2)
	$(whereis zfs | cut -d " " -f 2)
	$(whereis zhack | cut -d " " -f 2)
	$(whereis zinject | cut -d " " -f 2)
	$(whereis zpios | cut -d " " -f 2)
	$(whereis zpool | cut -d " " -f 2)
	$(whereis zstreamdump | cut -d " " -f 2)
	$(whereis ztest | cut -d " " -f 2)"

ZFS_MODS="zfs"

ZFS_MAN="
	${MAN}/man1/zhack.1.*
	${MAN}/man1/zpios.1.*
	${MAN}/man1/ztest.1.*
	${MAN}/man5/vdev_id.conf.5.*
	${MAN}/man5/zpool-features.5.*	
	${MAN}/man8/fsck.zfs.8.*
	${MAN}/man8/mount.zfs.8.*
	${MAN}/man8/vdev_id.8.*
	${MAN}/man8/zdb.8.*
	${MAN}/man8/zfs.8.*
	${MAN}/man8/zinject.8.*
	${MAN}/man8/zpool.8.* 
	${MAN}/man8/zstreamdump.8.*"

ZFS_UDEV="
	${UDEV}/rules.d/60-zvol.rules
	${UDEV}/rules.d/69-vdev.rules
	${UDEV}/rules.d/90-zfs.rules
	${UDEV}/vdev_id
	${UDEV}/zvol_id"
