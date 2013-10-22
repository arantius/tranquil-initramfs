#!/usr/bin/env python

# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

from .common import *

def print_vals():
	print("BASE: ", base.use_base)
	print("ZFS: ", zfs.use_zfs)
	print("LVM: ", lvm.use_lvm)
	print("RAID: ", raid.use_raid)
	print("LUKS: ", luks.use_luks)
	print("ADDON: ", addon.use_addon)
	print("KERNEL: ", kernel)	

# Checks to see if the binaries exist
def check_binaries():
	einfo("Checking binaries...")

	# Check base binaries (all initramfs have these)
	for x in base.base_bins:
		if not os.path.isfile(x):
			err_bin_dexi(x)

	# If using ZFS, check the zfs binaries
	if zfs.use_zfs == "1":
		eflag("Using ZFS")

		for x in zfs.zfs_bins:
			if not os.path.isfile(x):
				err_bin_dexi(x)

	# If using LVM, check the lvm binaries
	if lvm.use_lvm == "1":
		eflag("Using LVM")

		for x in lvm.lvm_bins:
			if not os.path.isfile(x):
				err_bin_dexi(x)

	# If using RAID, check the raid binaries
	if raid.use_raid == "1":
		eflag("Using RAID")

		for x in raid.raid_bins:
			if not os.path.isfile(x):
				err_bin_dexi(x)

	# If using LUKS, check the luks binaries
	if luks.use_luks == "1":
		eflag("Using LUKS")

		for x in luks.luks_bins:
			if not os.path.isfile(x):
				err_bin_dexi(x)

		for x in luks.gpg_bins:
			if not os.path.isfile(x):
				err_bin_dexi(x)

# Copy the required binary files into the initramfs
def copy_binaries():
	einfo("Copying binaries...")

	# Copy base binaries (all initramfs have these)
	for x in base.base_bins:
		if re.search('(?<=/)busybox', x):
			shutil.copy(x, lbin)
		else:
			ecp("--parents", x, temp)

	if zfs.use_zfs == "1":
		for x in zfs.zfs_bins:
			ecp("--parents", x, temp)

	if lvm.use_lvm == "1":
		for x in lvm.lvm_bins:
			if re.search('(?<=/)lvm.static', x):
				ecp("--parents", x, temp)
				os.rename(temp + x, temp + os.path.dirname(x) + "/lvm")
			else:
				ecp("--parents", x, temp)

	if raid.use_raid == "1":
		for x in raid.raid_bins:
			ecp("--parents", x, temp)

	if luks.use_luks == "1":
		for x in luks.luks_bins:
			ecp("--parents", x, temp)

		for x in luks.gpg_bins:
			ecp("--parents", x, temp)

# Get module dependencies
def get_modules():
	einfo("Gathering module dependencies...")

	global moddeps; moddeps = set()

	if addon.use_addon == "1":
		for x in addon.addon_mods:
			cmd = "modprobe -S " + kernel + " --show-depends " + x + " | awk -F ' ' '{print $2}'"
			cap = os.popen(cmd)

			for i in cap.readlines():
				moddeps.add(i.strip())

# Copies the modules to the initramfs
def copy_modules():
	einfo("Copying modules...")

	if moddeps:
		# Making sure that the dependencies are up to date
		call(["depmod", kernel])

		if addon.use_addon == "1":
			for x in moddeps:
				ecp("--parents", "-r", x, temp)

		# Compress the modules and update dependencies
		do_modules()
	else:
		# No modules will be used. Deleting the empty tree in the temporary directory
		if os.path.exists(lmodules):
			shutil.rmtree(temp + "/lib")

# Copy the documentation
def copy_docs():
	einfo("Copying documentation...")

	if zfs.use_zfs == "1":
		for x in zfs.zfs_man:
			cmd = "mkdir -p `dirname " + temp + "/" + x + "`"
			call(cmd, shell=True)
			ecp("-r", glob.glob(x)[0], temp + "/" + glob.glob(x)[0])

# Copy the udev rules
def copy_udev():
	einfo("Copying udev rules...")

	if zfs.use_zfs == "1":
		for x in zfs.zfs_udev:
			cmd = "mkdir -p `dirname " + temp + "/" + x + "`"
			call(cmd, shell=True)
			ecp("-r", glob.glob(x)[0], temp + "/" + glob.glob(x)[0])

# Copy any other files that need to be copied
def copy_other():
	einfo("Copying other files...")

	if base.use_base == "1":
		os.makedirs(temp + "/etc/bash")

		shutil.copy("/etc/bash/bashrc", temp + "/etc/bash/")
		shutil.copy("/etc/DIR_COLORS", temp + "/etc/")

		# Remove incompatible stuff from bashrc (like --colour=auto)
		cmd = "sed -i '69, 71d' " + temp + "/etc/bash/bashrc"
		call(cmd, shell=True)

	if luks.use_luks == "1":
		for x in luks.gpg_files:
			ecp("--parents", x, temp)

# Gets dependency list for parameter
def get_dlist(f):
	global filedeps

	cmd = "ldd " + f + " | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}'"
	cap = os.popen(cmd)

	for i in cap.readlines():
		filedeps.add(i.strip())
	
def do_deps():
	einfo("Getting and copying dependencies...")

	global filedeps; filedeps = set()

	# Get the interpreter name that is on this system
	r = check_output("ls " + lib64 + "/ld-linux-x86-64.so*", universal_newlines=True, shell=True).strip()

	# Add intepreter to deps since everything will depend on it
	filedeps.add(r)

	for x in base.base_bins:
		get_dlist(x)

	if zfs.use_zfs == "1":
		for x in zfs.zfs_bins:
			get_dlist(x)

	if luks.use_luks == "1":
		for x in luks.luks_bins:
			get_dlist(x)

		for x in luks.gpg_bins:
			get_dlist(x)
	
	# Copy all the dependencies of the binary files into the initramfs
	for x in filedeps:
		ecp("--parents", x, temp)
