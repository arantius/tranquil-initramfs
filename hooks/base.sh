# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Required Binaries, Modules, and other files
USE_BASE="1"

# Detect where the binaries are
BASE_BINS="
        ${PLUGINS}/busybox/busybox
        $(whereis bash | cut -d " " -f 2)
        $(whereis kmod | cut -d " " -f 2)"

# kmod symlinks
KMOD_SYM="depmod insmod lsmod modinfo modprobe rmmod"
