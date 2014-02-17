#!/usr/bin/env python

# Copyright (C) 2012-2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Temporary fix for detecting location of kmod until I redesign the app.
# The hooks/* files should stay away from performing logic
import subprocess

# Detect where kmod is (Gentoo = /bin, Funtoo = /sbin)
def find_kmod():
	p1 = subprocess.Popen(
	["whereis", "kmod"],
	stdout=subprocess.PIPE,
	universal_newlines=True)

	p2 = subprocess.Popen(
	["cut", "-d", " ", "-f", "2"],
	stdin=p1.stdout, stdout=subprocess.PIPE,
	universal_newlines=True)

	out = p2.stdout.readlines()

	if out:
		return out[0].strip()
	else:
		print("Unable to find kmod")
		quit(1)

kmod_path = find_kmod()

files = [
	# sys-apps/busybox
	"/bin/busybox",

	# sys-apps/kmod
	kmod_path,

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

kmod_links = [ "depmod", "insmod", "lsmod", "modinfo", "modprobe", "rmmod" ]
