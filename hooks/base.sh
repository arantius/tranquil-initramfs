# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# Distributed under the GPLv2 which can be found in the COPYING file.

# Required Binaries, Modules, and other files
USE_BASE="1"

# Detect where the binaries are
BASE_BINS="
        ${PLUGINS}/busybox/busybox
        $(whereis bash | cut -d " " -f 2)
        $(whereis kmod | cut -d " " -f 2)"

# Files related to Bash
BASH_FILES="
	${ETC}/bash/bashrc
	${ETC}/DIR_COLORS"

# kmod symlinks
KMOD_SYM="depmod insmod lsmod modinfo modprobe rmmod"
