#!/usr/bin/env python

# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from ..libs.variables import *

# Enable/Disable Hook
use_lvm = "0"

if os.path.isfile(sbin + "/lvm.static"):
	lvm_bins = [ sbin + "/lvm.static" ]
elif os.path.isfile(sbin + "/lvm"):
	lvm_bins = [ sbin + "/lvm" ]
else:
	lvm_bins = []

lvm_files = [ "/etc/lvm/lvm.conf" ]

lvm_man = [
        man + "/man5/lvm.conf.5.*",
        man + "/man8/dmeventd.8.*",
        man + "/man8/dmsetup.8.*",
        man + "/man8/fsadm.8.*",
        man + "/man8/lvchange.8.*",
        man + "/man8/lvconvert.8.*",
        man + "/man8/lvcreate.8.*",
        man + "/man8/lvdisplay.8.*",
        man + "/man8/lvextend.8.*",
        man + "/man8/lvm.8.*",
        man + "/man8/lvm2create_initrd.8.*",
        man + "/man8/lvmchange.8.*",
        man + "/man8/lvmconf.8.*",
        man + "/man8/lvmdiskscan.8.*",
        man + "/man8/lvmdump.8.*",
        man + "/man8/lvmsadc.8.*",
        man + "/man8/lvmsar.8.*",
        man + "/man8/lvreduce.8.*",
        man + "/man8/lvremove.8.*",
        man + "/man8/lvrename.8.*",
        man + "/man8/lvresize.8.*",
        man + "/man8/lvs.8.*",
        man + "/man8/lvscan.8.*",
        man + "/man8/pvchange.8.*",
        man + "/man8/pvck.8.*",
        man + "/man8/pvcreate.8.*",
        man + "/man8/pvdisplay.8.*",
        man + "/man8/pvmove.8.*",
        man + "/man8/pvremove.8.*",
        man + "/man8/pvresize.8.*",
        man + "/man8/pvs.8.*",
        man + "/man8/pvscan.8.*",
        man + "/man8/vgcfgbackup.8.*",
        man + "/man8/vgcfgrestore.8.*",
        man + "/man8/vgchange.8.*",
        man + "/man8/vgck.8.*",
        man + "/man8/vgconvert.8.*",
        man + "/man8/vgcreate.8.*",
        man + "/man8/vgdisplay.8.*",
        man + "/man8/vgexport.8.*",
        man + "/man8/vgextend.8.*",
        man + "/man8/vgimport.8.*",
        man + "/man8/vgimportclone.8.*",
        man + "/man8/vgmerge.8.*",
        man + "/man8/vgmknodes.8.*",
        man + "/man8/vgreduce.8.*",
        man + "/man8/vgremove.8.*",
        man + "/man8/vgrename.8.*",
        man + "/man8/vgs.8.*",
        man + "/man8/vgscan.8.*",
        man + "/man8/vgsplit.8.*"]
