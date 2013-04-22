# Simplified BSD License
#
# Copyright (C) 2013 Jonathan Vasquez <jvasquez1011@gmail.com> 
# All Rights Reserved
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met: 
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer. 
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution. 
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Toggle Flags
_USE_ZFS="1"
_USE_MODULES="1"

# Set the kernel we will be using here
do_kernel

# Required Binaries, Modules, and other files
_ZFS_BINS="${_USR_BIN}/hostid \
	   ${_SBIN}/fsck.zfs \
	   ${_SBIN}/mount.zfs \
	   ${_SBIN}/zdb \
	   ${_SBIN}/zfs \
	   ${_SBIN}/zhack \
	   ${_SBIN}/zinject \
	   ${_SBIN}/zpios \
	   ${_SBIN}/zpool \
	   ${_SBIN}/zstreamdump \
	   ${_SBIN}/ztest"

_ZFS_MODS="${_MODULES}/extra/spl/spl.ko \
	   ${_MODULES}/extra/avl/zavl.ko \
	   ${_MODULES}/extra/nvpair/znvpair.ko \
	   ${_MODULES}/extra/unicode/zunicode.ko \
	   ${_MODULES}/extra/zcommon/zcommon.ko \
	   ${_MODULES}/extra/zfs/zfs.ko"

_ZFS_MAN="${_MAN}/man1/zhack.1.bz2 \
          ${_MAN}/man1/zpios.1.bz2 \
          ${_MAN}/man1/ztest.1.bz2 \
          ${_MAN}/man5/vdev_id.conf.5.bz2 \
          ${_MAN}/man5/zpool-features.5.bz2 \
          ${_MAN}/man8/fsck.zfs.8.bz2 \
          ${_MAN}/man8/mount.zfs.8.bz2 \
	  ${_MAN}/man8/vdev_id.8.bz2 \
	  ${_MAN}/man8/zdb.8.bz2 \
	  ${_MAN}/man8/zfs.8.bz2 \
          ${_MAN}/man8/zinject.8.bz2 \
	  ${_MAN}/man8/zpool.8.bz2 \
	  ${_MAN}/man8/zstreamdump.8.bz2"

_ZFS_UDEV="${_UDEV}/rules.d/60-zvol.rules \
	   ${_UDEV}/rules.d/69-vdev.rules \
	   ${_UDEV}/rules.d/90-zfs.rules \
	   ${_UDEV}/vdev_id \
	   ${_UDEV}/zvol_id"
