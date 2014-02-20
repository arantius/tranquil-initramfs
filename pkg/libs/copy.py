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

from pkg.libs.toolkit import Toolkit
from pkg.libs.variables import Variables

import os
import re

""" Globally Available Tools """
tools = Toolkit()

class Copy(object):
	# List of binaries (That will be 'ldd'ed later)
	binset = set()

	# List of modules that will be compressed
	modset = set()

	def __init__(self, core, var):
		#print("Kernel: " + var.kernel)
		self.core = core
		self.var = var
		#print("CKernel: " + self.core.var.kernel)

	# Checks to see if the binaries exist, if not then emerge
	def check_binaries(self):
		tools.einfo("Checking required files ...")

		# Check required base files
		for f in self.core.base.files:
			if not os.path.exists(f):
				tools.err_bin_dexi(f)
			else:
				print("Exists: " + f)

		# Check required zfs files
		if self.core.zfs.use == "1":
			tools.eflag("Using ZFS")
			for f in self.core.zfs.files:
				if not os.path.exists(f):
					tools.err_bin_dexi(f)
				else:
					print("Exists: " + f)

		# Check required lvm files
		if self.core.lvm.use == "1":
			tools.eflag("Using LVM")
			for f in self.core.lvm.files:
				if not os.path.exists(f):
					tools.err_bin_dexi(f)
				else:
					print("Exists: " + f)

		# Check required raid files
		if self.core.raid.use == "1":
			tools.eflag("Using RAID")
			for f in self.core.raid.files:
				if not os.path.exists(f):
					tools.err_bin_dexi(f)
				else:
					print("Exists: " + f)

		# Check required luks files
		if self.core.luks.use == "1":
			tools.eflag("Using LUKS")
			for f in self.core.luks.files:
				if not os.path.exists(f):
					tools.err_bin_dexi(f)
				else:
					print("Exists: " + f)

	# Installs the packages
	def install():
		tools.einfo("Copying required files...")

		for file in self.core.base.files:
			emerge(file)

		if self.core.zfs.use == "1":
			for file in self.core.zfs.files:
				emerge(file)

		if self.core.lvm.use == "1":
			for file in self.core.lvm.files:
				emerge(file)
		
		if self.core.raid.use == "1":
			for file in self.core.raid.files:
				emerge(file)

		if self.core.luks.use == "1":
			for file in self.core.luks.files:
				emerge(file)

	# Filters and installs a package into the initramfs
	def emerge(file):
		global binset
		global modset

		# If the application is a binary, add it to our binary set
		try:
			lcmd = subprocess.check_output("file " + file.strip() +
			" | grep \"linked\"", universal_newlines=True, shell=True).strip()

			binset.add(file)
		except subprocess.CalledProcessError:
			pass

		# Copy the file into the initramfs
		tools.ecopy(file)

	# Copy modules and their dependencies
	def copy_modules():
		tools.einfo("Copying modules...")

		global modset
		moddeps = set()

		# Build the list of module dependencies
		if self.core.addon.use == "1":
			# Checks to see if all the modules in the list exist
			for x in self.core.addon.modules:
				try:
					cmd = "find " + common.modules + " -iname \"" + x + \
					".ko\" | grep " + x + ".ko"
					
					result = subprocess.check_output(cmd, universal_newlines=True,
						 shell=True).strip()

					modset.add(result)
				except subprocess.CalledProcessError:
					err_mod_dexi(x)

		# If a kernel has been set, try to update the module dependencies
		# database before searching it
		if common.kernel:
			result = subprocess.call(["depmod", common.kernel])

			if result == 1:
				die("Error updating module dependency database!")

		# Get the dependencies for all the modules in our set
		for x in modset:
			# Get only the name of the module
			match = re.search('(?<=/)\w+.ko', x)

			if match:
				sx = match.group().split(".")[0]
				
				cmd = "modprobe -S " + common.kernel + " --show-depends " + sx + \
					  " | awk -F ' ' '{print $2}'"
				
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
	def copy_deps():
		tools.einfo("Copying library dependencies...")

		bindeps = set()

		# Get the interpreter name that is on this system
		r = subprocess.check_output("ls " + common.variables.lib64 + 
			"/ld-linux-x86-64.so*", universal_newlines=True, shell=True).strip()

		# Add intepreter to deps since everything will depend on it
		bindeps.add(r)

		# Get the dependencies for the binaries we've collected and add them to
		# our bindeps set. These will all be copied into the initramfs later.
		for b in binset:
			cmd = "ldd " + b.strip() + " | awk -F '=>' '{print $2}' \
			| sed '/^ *$/d' | awk -F '(' '{print $1}'"
			cap = os.popen(cmd)

			for j in cap.readlines():
				bindeps.add(j.strip())

			cap.close()

		# Copy all the dependencies of the binary files into the initramfs
		for x in bindeps:
			tools.ecopy(x)
