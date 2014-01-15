#!/usr/bin/env python

# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import shutil
import glob

from .variables import *
from subprocess import call, Popen, PIPE, STDOUT

from ..hooks import base
from ..hooks import zfs
from ..hooks import lvm
from ..hooks import raid
from ..hooks import luks
from ..hooks import addon

kernel = ""
modules = ""
lmodules = ""
initrd = "initrd"
choice = ""

# Prints the header of the application
def print_header():
	call(["echo", "-e", "\e[1;33m-----------------------------------\e[0;m"])
	call(["echo", "-e", "\e[1;33m| " + name + " - v" + version + "\e[0;m"])
	call(["echo", "-e", "\e[1;33m| Author: " + contact + "\e[0;m"])
	call(["echo", "-e", "\e[1;33m| Distributed under the " + license + "\e[0;m"])
	call(["echo", "-e", "\e[1;33m-----------------------------------\e[0;m"])

# Prints the menu and accepts user choice
def print_menu():
	global choice

	# If the user didn't pass an option through the command line,
	# then ask them which initramfs they would like to generate.
	if not choice:
		einfo("Which initramfs would you like to generate:")
		print_options()
		choice = eqst("Current choice [1]: ")

	# All initramfs will have the base
	base.use_base = "1"
	addon.use_addon = "1"

	if choice == "1" or choice == "":
		zfs.use_zfs = "1"

		# Add the 'zfs' kernel module to the addon modules list
		addon.addon_mods.append("zfs")
	elif choice == "2":
		lvm.use_lvm = "1"
	elif choice == "3":
		raid.use_raid = "1"
	elif choice == "4":
		raid.use_raid = "1"
		lvm.use_lvm = "1"
	elif choice == "5":
		pass
	elif choice == '6':
		luks.use_luks = "1"
		zfs.use_zfs = "1"

		# Add the 'zfs' kernel module to the addon modules list
		addon.addon_mods.append("zfs")
	elif choice == "7":
		luks.use_luks = "1"
		lvm.use_lvm = "1"
	elif choice == "8":
		luks.use_luks = "1"
		raid.use_raid = "1"
	elif choice == "9":
		luks.use_luks = "1"
		raid.use_raid = "1"
		lvm.use_lvm = "1"
	elif choice == "10":
		luks.use_luks = "1"
	elif choice == '11':
		ewarn("Exiting.")
		quit()
	else:
		ewarn("Invalid Option. Exiting.")
		quit()

# Prints the available options
def print_options():
	eline()
	eopt("1. ZFS")
	eopt("2. LVM")
	eopt("3. RAID")
	eopt("4. LVM on RAID")
	eopt("5. Normal Boot")
	eopt("6. Encrypted ZFS")
	eopt("7. Encrypted LVM")
	eopt("8. Encrypted RAID")
	eopt("9. Encrypted LVM on RAID")
	eopt("10. Encrypted Normal")
	eopt("11. Exit Program")
	eline()

# Ask the user if they want to use their current kernel, or another one
def do_kernel():
	global kernel
	global modules
	global lmodules
	global initrd

	if not kernel:
		currentKernel = check_output(["uname", "-r"], universal_newlines=True).strip()	
		eline(); x = "Do you want to use the current kernel: " + currentKernel + " [Y/n]: "
		choice = eqst(x); eline()

		if choice == 'y' or choice == 'Y' or choice == '':
			kernel = currentKernel
		elif choice == 'n' or choice == 'N':
			kernel = eqst("Please enter the kernel name: "); eline()

			if kernel == "":
				die("You didn't enter a kernel. Exiting...")
		else:
			die("Invalid Option. Exiting.")

	# Set modules path to correct location and sets kernel name for initramfs
	modules = "/lib/modules/" + kernel + "/"
	lmodules = temp + "/" + modules
	initrd = "initrd-" + kernel

	# Check modules directory
	check_mods_dir()

# Check to make sure the kernel modules directory exists
def check_mods_dir():
	x = "Checking to see if " + modules + " exists..."
	einfo(x)

	if not os.path.exists(modules):
		die("Modules directory doesn't exist.")

# Make sure that the arch is x86_64
def get_arch():
	if arch != "x86_64":
		die("Your architecture isn't supported. Exiting.")

# Message for displaying the starting generating event
def print_start():
	eline(); einfo("[ Starting ]"); eline()

# Check to see if the temporary directory exists, if it does, delete it for a fresh start
def clean():
	# Go back to the original working directory so that we are
	# completely sure that there will be no inteference cleaning up.
	os.chdir(home)

	if os.path.exists(temp):
		shutil.rmtree(temp)

		if os.path.exists(temp):
			ewarn("Failed to delete the " + temp + " directory. Exiting.")
			quit()

# Create the base directory structure for the initramfs
def create_dirs():
	einfo("Creating directory structure...")

	# Make base directories
	for x in cdirs:
		os.makedirs(x)

	# If we are using kernel modules, then make the kernel modules directory
	if lmodules:
		os.makedirs(lmodules)
	
	# Make ZFS specific directories
	if zfs.use_zfs == "1":
		os.makedirs(temp + "/etc/zfs")

	# Make LUKS specific directories
	if luks.use_luks == "1":
		os.makedirs(temp + "/mnt/key")

# Checks to see if the preliminary binaries exist
def check_prelim_binaries():
	einfo("Checking preliminary binaries...")

	for x in prel_bin:
		if not os.path.isfile(x):
			err_bin_dexi(x, "app-arch/cpio")

# Compresses the kernel modules and generates modprobe table
def do_modules():
	einfo("Compressing kernel modules...")

	cmd = "find " + lmodules + " -name " + "*.ko"
	cap = os.popen(cmd)

	for x in cap:
		cmd = "gzip " + x.strip()
		call(cmd, shell=True)
	
	einfo("Generating modprobe information...")

	# Copy modules.order and modules.builtin just so depmod doesn't spit out warnings. -_-
	ecp(modules + "/modules.{order,builtin}", lmodules)
	result = call(["depmod", "-b", temp, kernel])

	if result != 0:
		die("Either you don't have depmod, or another problem occured")

# Create the required symlinks to it
def create_links():
	einfo("Creating symlinks...")

	# Needs to be from this directory so that the links are relative
	os.chdir(lbin)

	# Create 'sh' symlink to 'bash'
	os.symlink("bash", "sh")

	# Create busybox links
	call([lbin + "/busybox", "--install", "."])

	# Go to the directory where kmod is in
	if os.path.isfile(lsbin + "/kmod"):
		os.chdir(lsbin)
	elif os.path.isfile(lbin + "/kmod"):
		os.chdir(lbin)

	# Create module loading links to 'kmod' (from the lbin dir)
	for i in base.kmod_sym:
		os.symlink("kmod", i)

# This function copies and sets up any files needed. mtab, init, zpool.cache
def config_files():
	einfo("Configuring files...")

	call(["touch", temp + "/etc/mtab"])

	if not os.path.isfile(temp + "/etc/mtab"):
		die("Error creating the mtab file. Exiting.")

	# Copy init functions
	shutil.copytree(home + "/files/libraries/", temp + "/libraries")

	# Copy the init script
	shutil.copy(home + "/files/init", temp)

	# Give execute permissions to the script
	call(["chmod", "u+x", temp + "/init"])

	if not os.path.isfile(temp + "/init"):
		die("Error creating the init file. Exiting.")

	# Sets initramfs script version number
	call(["sed", "-i", "-e", "18s/0/" + version + "/", temp + "/init"])

	# Any last substitutions or additions/modifications should be done here
	if zfs.use_zfs == "1":
		# Enable ZFS in the init if ZFS is being used
		call(["sed", "-i", "-e", "13s/0/1/", temp + "/init"])

		# Copy the /etc/modprobe.d/zfs.conf file if it exists
		if os.path.isfile("/etc/modprobe.d/zfs.conf"):
			os.makedirs(temp + "/etc/modprobe.d")
			shutil.copy("/etc/modprobe.d/zfs.conf", temp + "/etc/modprobe.d")

	# Enable RAID in the init if RAID is being used
	if raid.use_raid == "1":
		call(["sed", "-i", "-e", "14s/0/1/", temp + "/init"])

	# Enable LVM in the init if LVM is being used
	if lvm.use_lvm == "1":
		call(["sed", "-i", "-e", "15s/0/1/", temp + "/init"])

	# Enable LUKS in the init if LUKS is being used
	if luks.use_luks == "1":
		call(["sed", "-i", "-e", "16s/0/1/", temp + "/init"])
	
	if addon.use_addon == "1":
		call(["sed", "-i", "-e", "18s/\"\"/\"" + 
		" ".join(addon.addon_mods) + "\"/", temp + "/libraries/common.sh"])

# Create the solution
def create():
	einfo("Creating the initramfs...")

	# The find command must use the `find .` and not `find ${T}`
        # because if not, then the initramfs layout will be prefixed with
        # the ${T} path.
	os.chdir(temp)

	call(["find . -print0 | cpio -o --null --format=newc | gzip -9 > " +  home + "/" + initrd], shell=True)

	if not os.path.isfile(home + "/" + initrd):
		die("Error creating the initramfs. Exiting.")

# Clean up and exit after a successful build
def clean_exit():
	eline(); einfo("[ Complete ]"); eline()
	clean()

	einfo("Please copy the " + initrd + " to your /boot directory")
	quit()

####### Message Functions #######

# Used for displaying information
def einfo(x):
	call(["echo", "-e", "\e[1;32m>>>\e[0;m " + x ])

# Used for input (questions)
def eqst(x):
	#choice = input(call(["echo", "-en", "\e[1;37m>>>\e[;0m " + x ]))
	choice = input(x)
	return choice

# Used for warnings
def ewarn(x):
	call(["echo", "-e", "\e[1;33m>>>\e[0;m " + x])

# Used for flags (aka using zfs, luks, etc)
def eflag(x):
	call(["echo", "-e", "\e[1;34m>>>\e[0;m " + x])

# Used for options
def eopt(x):
	call(["echo", "-e", "\e[1;36m>>>\e[0;m " + x])

# Used for errors
def die(x):
	eline()
	call(["echo", "-e", "\e[1;31m>>>\e[0;m " + x])
	eline()
	clean()
	quit(1)

# Prints empty line
def eline():
	print("")

# Error Function: Binary doesn't exist
def err_bin_dexi(x, *y):
	if y:
		die("Binary: " + x + " doesn't exist. Please emerge " + y[0] + ". Exiting.")
	else:
		die("Binary: " + x + " doesn't exist. Exiting.")

# Error Function: Module doesn't exist
def err_mod_dexi(x):
	die("Module: " + x + " doesn't exist. Exiting.")

# Copies functions with specific flags
def ecp(*x):
	if x:
		cmd = "cp -afL"

		for i in x:
			cmd = cmd + " " + i
			
		call(cmd, shell=True)
