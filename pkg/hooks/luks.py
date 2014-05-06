# Copyright 2012-2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pkg.hooks.hook import Hook

class LUKS(Hook):
	# Required Files
	files = [
		"/sbin/cryptsetup",
		"/usr/bin/gpg",
		"/usr/bin/gpg-agent",
		"/usr/share/gnupg/gpg-conf.skel",
	]
