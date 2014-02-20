#!/usr/bin/env python

"""
Copyright (C) 2012-2014 Jonathan Vasquez <fearedbliss@funtoo.org>

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

class Base(object):
	files = [
		# sys-apps/busybox
		"/bin/busybox",

		# sys-apps/kmod
		#kmod_path,
		"/sbin/kmod",

		# app-shells/bash
		"/bin/bash",
		"/etc/bash/bashrc",
		"/etc/DIR_COLORS",
		"/etc/profile",

		# sys-apps/grep
		"/bin/egrep",
		"/bin/fgrep",
		"/bin/grep",

		# sys-apps/util-linux
		"/bin/mount",
		"/bin/umount",
		"/bin/dmesg",
		"/sbin/blkid",
		"/sbin/switch_root",
	]

	kmod_links = [ "depmod", "insmod", "lsmod",
	               "modinfo", "modprobe", "rmmod" ]
