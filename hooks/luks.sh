# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Toggle Flags
USE_LUKS="1"

# Required Binaries, Modules, and other files
LUKS_BINS="$(whereis cryptsetup | cut -d " " -f 2)"

LUKS_MAN="${MAN}/man8/cryptsetup.8.*"

GPG_BINS="
	$(whereis gpg | cut -d " " -f 2)
	$(whereis gpg-agent | cut -d " " -f 2)"

GPG_FILES="${USHARE}/gnupg/gpg-conf.skel"
