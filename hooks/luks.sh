# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# Distributed under the GPLv2 which can be found in the COPYING file.

# Toggle Flags
USE_LUKS="1"

# Required Binaries, Modules, and other files
LUKS_BINS="${SBIN}/cryptsetup"

GPG_BINS="
	${UBIN}/gpg
	${UBIN}/gpg-agent"

GPG_FILES="${USHARE}/gnupg/gpg-conf.skel"
