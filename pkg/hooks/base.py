# Copyright 2012-2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pkg.hooks.hook import Hook
from pkg.libs.toolkit import Toolkit as tools

class Base(Hook):
	def __init__(self):
		Hook.__init__(self)

		# Activate the Base implicitly since it will always be included in all initramfs
		self.use = 1

		# Set the kmod path for this system
		self.kmod_path = tools.find_prog("kmod")

		self.files = [
			# sys-apps/busybox
			"/bin/busybox",

			# sys-apps/kmod
			self.kmod_path,

			# app-shells/bash
			"/bin/bash",
			"/etc/bash/bashrc",
			"/etc/DIR_COLORS",
			"/etc/profile",

			# sys-apps/grep
			"/bin/egrep",
			"/bin/fgrep",
			"/bin/grep",
		]

		self.kmod_links = [
			"depmod",
			"insmod",
			"lsmod",
			"modinfo",
			"modprobe",
			"rmmod",
		]

	# Returns the kmod path
	def get_kmod_path(self):
		return self.kmod_path

	# Returns the kmod links
	def get_kmod_links(self):
		return self.kmod_links
