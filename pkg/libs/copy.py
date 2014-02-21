#!/usr/bin/env python

"""
# Copyright (C) 2012-2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

from subprocess import call
from subprocess import check_output
from subprocess import Popen
from subprocess import PIPE
from subprocess import CalledProcessError

from pkg.libs.toolkit import Toolkit
from pkg.libs.variables import Variables

import os
import re

""" Globally Available Resources """
tools = Toolkit()
var = Variables()

class Copy(object):
	def __init__(self, core):
		self.core = core

		# List of binaries (That will be 'ldd'ed later)
		self.binset = set()

		# List of modules that will be compressed
		self.modset = set()

	# Checks to see if the binaries exist, if not then emerge
	def check_binaries(self):
		tools.einfo("Checking required files ...")

		# Check required base files
		for f in self.core.base.files:
			if not os.path.exists(f):
				tools.err_bin_dexi(f)

		# Check required zfs files
		if self.core.zfs.use == "1":
			tools.eflag("Using ZFS")
			for f in self.core.zfs.files:
				if not os.path.exists(f):
					tools.err_bin_dexi(f)

		# Check required lvm files
		if self.core.lvm.use == "1":
			tools.eflag("Using LVM")
			for f in self.core.lvm.files:
				if not os.path.exists(f):
					tools.err_bin_dexi(f)

		# Check required raid files
		if self.core.raid.use == "1":
			tools.eflag("Using RAID")
			for f in self.core.raid.files:
				if not os.path.exists(f):
					tools.err_bin_dexi(f)

		# Check required luks files
		if self.core.luks.use == "1":
			tools.eflag("Using LUKS")
			for f in self.core.luks.files:
				if not os.path.exists(f):
					tools.err_bin_dexi(f)

	# Installs the packages
	def install(self):
		tools.einfo("Copying required files ...")

		for f in self.core.base.files:
			self.emerge(f)

		if self.core.zfs.use == "1":
			for f in self.core.zfs.files:
				self.emerge(f)

		if self.core.lvm.use == "1":
			for f in self.core.lvm.files:
				self.emerge(f)
		
		if self.core.raid.use == "1":
			for f in self.core.raid.files:
				self.emerge(f)

		if self.core.luks.use == "1":
			for f in self.core.luks.files:
				self.emerge(f)

	# Filters and installs a package into the initramfs
	def emerge(self, afile):
		# If the application is a binary, add it to our binary set
		try:
			lcmd = check_output("file " + afile.strip() +
			" | grep \"linked\"", universal_newlines=True, shell=True).strip()

			self.binset.add(afile)
		except CalledProcessError:
			pass

		# Copy the file into the initramfs
		tools.ecopy(afile)

	# Copy modules and their dependencies
	def copy_modules(self):
		tools.einfo("Copying modules ...")

		moddeps = set()

		# Build the list of module dependencies
		if self.core.addon.use == "1":
			# Checks to see if all the modules in the list exist
			for x in self.core.addon.modules:
				try:
					cmd = "find " + self.core.modules + " -iname \"" + x + \
					".ko\" | grep " + x + ".ko"
					
					result = check_output(cmd, universal_newlines=True,
					         shell=True).strip()

					self.modset.add(result)
				except CalledProcessError:
					tools.err_mod_dexi(x)

		# If a kernel has been set, try to update the module dependencies
		# database before searching it
		if self.core.kernel:
			result = call(["depmod", self.core.kernel])

			if result == 1:
				tools.die("Error updating module dependency database!")

		# Get the dependencies for all the modules in our set
		for x in self.modset:
			# Get only the name of the module
			match = re.search('(?<=/)\w+.ko', x)

			if match:
				sx = match.group().split(".")[0]
				
				cmd = "modprobe -S " + self.core.kernel + " --show-depends " + \
				sx + " | awk -F ' ' '{print $2}'"
				
				cap = os.popen(cmd)

				for i in cap.readlines():
					moddeps.add(i.strip())

				cap.close()

		# Copy the modules/dependencies
		if moddeps:
			for x in moddeps:
				tools.ecopy(x)

			# Compress the modules and update module dependency database
			# inside the initramfs
			self.core.do_modules()

	# Gets the library dependencies for all our binaries and copies them
	# into our initramfs.
	def copy_deps(self):
		tools.einfo("Copying library dependencies ...")

		bindeps = set()

		# Get the interpreter name that is on this system
		r = check_output("ls " + var.lib64 + "/ld-linux-x86-64.so*",
		    universal_newlines=True, shell=True).strip()

		# Add intepreter to deps since everything will depend on it
		bindeps.add(r)

		# Get the dependencies for the binaries we've collected and add them to
		# our bindeps set. These will all be copied into the initramfs later.
		for b in self.binset:
			cmd = "ldd " + b.strip() + " | awk -F '=>' '{print $2}' \
			| sed '/^ *$/d' | awk -F '(' '{print $1}'"

			cap = os.popen(cmd)

			for j in cap.readlines():
				bindeps.add(j.strip())

			cap.close()

		# Copy all the dependencies of the binary files into the initramfs
		for x in bindeps:
			tools.ecopy(x)
