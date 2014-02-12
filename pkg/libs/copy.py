#!/usr/bin/env python

# Copyright (C) 2012-2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import subprocess
import re

from . import common

# List of binaries (That will be 'ldd'ed later)
binset = set()

# List of modules that will be compressed
modset = set()

# Checks to see if the binaries exist, if not then emerge
def check_binaries():
	common.einfo("Checking required files...")

	# Check required base files
	for file in common.base.files:
		if not os.path.exists(file):
			err_bin_dexi(file)

	# Check required zfs files
	if common.zfs.use == "1":
		common.eflag("Using ZFS")
		for file in common.zfs.files:
			if not os.path.exists(file):
				err_bin_dexi(file)

	# Check required lvm files
	if common.lvm.use == "1":
		common.eflag("Using LVM")
		for file in common.lvm.files:
			if not os.path.exists(file):
				err_bin_dexi(file)

	# Check required raid files
	if common.raid.use == "1":
		common.eflag("Using RAID")
		for file in common.raid.files:
			if not os.path.exists(file):
				err_bin_dexi(file)

	# Check required luks files
	if common.luks.use == "1":
		common.eflag("Using LUKS")
		for file in common.luks.files:
			if not os.path.exists(file):
				err_bin_dexi(file)

# Installs the packages
def install():
	common.einfo("Copying required files...")

	for file in common.base.files:
		emerge(file)

	if common.zfs.use == "1":
		for file in common.zfs.files:
			emerge(file)

	if common.lvm.use == "1":
		for file in common.lvm.files:
			emerge(file)
	
	if common.raid.use == "1":
		for file in common.raid.files:
			emerge(file)

	if common.luks.use == "1":
		for file in common.luks.files:
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
	common.ecopy(file)

# Copy modules and their dependencies
def copy_modules():
	common.einfo("Copying modules...")

	global modset
	moddeps = set()

	# Build the list of module dependencies
	if common.addon.use == "1":
		# Checks to see if all the modules in the list exist
		for x in common.addon.modules:
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
			common.ecopy(x)

		# Compress the modules and update module dependency database
		# inside the initramfs
		common.do_modules()

# Gets the library dependencies for all our binaries and copies them
# into our initramfs.
def copy_deps():
	common.einfo("Copying library dependencies...")

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
		common.ecopy(x)
