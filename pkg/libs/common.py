#!/usr/bin/env python

# Copyright (C) 2012-2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import subprocess
import os
import shutil

from pkg.libs.variables import Variables
from pkg.libs.toolkit import Toolkit

from pkg.hooks import base
from pkg.hooks import zfs
from pkg.hooks import lvm
from pkg.hooks import raid
from pkg.hooks import luks
from pkg.hooks import addon

kernel = ""
modules = ""
lmodules = ""
initrd = "initrd"
choice = ""

tools = Toolkit()
var = Variables()

# Prints the header of the application
def print_header():
	subprocess.call(["echo", "-e", 
		"\e[1;33m-----------------------------------\e[0;m"])
	
	subprocess.call(["echo", "-e", "\e[1;33m| " + var.name + 
		" - v" + var.version + "\e[0;m"])

	subprocess.call(["echo", "-e", "\e[1;33m| Author: " + var.contact +
		"\e[0;m"])
	
	subprocess.call(["echo", "-e", "\e[1;33m| Distributed under the " + 
		var.license + "\e[0;m"])
	
	subprocess.call(["echo", "-e", 
		"\e[1;33m-----------------------------------\e[0;m"])

# Prints the menu and accepts user choice
def print_menu():
	# If the user didn't pass an option through the command line,
	# then ask them which initramfs they would like to generate.
	global choice

	if not choice:
		tools.einfo("Which initramfs would you like to generate:")
		print_options()
		choice = tools.eqst("Current choice [1]: ")

	# Enable the addons if the addon.mods is not empty
	if addon.modules:
		addon.use = "1"

	if choice == "1" or choice == "":
		zfs.use = "1"
		addon.use = "1"
		addon.modules.append("zfs")
	elif choice == "2":
		lvm.use = "1"
	elif choice == "3":
		raid.use = "1"
	elif choice == "4":
		raid.use = "1"
		lvm.use = "1"
	elif choice == "5":
		pass
	elif choice == '6':
		luks.use = "1"
		zfs.use = "1"
		addon.use = "1"
		addon.modules.append("zfs")
	elif choice == "7":
		luks.use = "1"
		lvm.use = "1"
	elif choice == "8":
		luks.use = "1"
		raid.use = "1"
	elif choice == "9":
		luks.use = "1"
		raid.use = "1"
		lvm.use = "1"
	elif choice == "10":
		luks.use = "1"
	elif choice == '11':
		tools.ewarn("Exiting.")
		quit()
	else:
		tools.ewarn("Invalid Option. Exiting.")
		quit()

# Prints the available options
def print_options():
	tools.eline()
	tools.eopt("1. ZFS")
	tools.eopt("2. LVM")
	tools.eopt("3. RAID")
	tools.eopt("4. LVM on RAID")
	tools.eopt("5. Normal Boot")
	tools.eopt("6. Encrypted ZFS")
	tools.eopt("7. Encrypted LVM")
	tools.eopt("8. Encrypted RAID")
	tools.eopt("9. Encrypted LVM on RAID")
	tools.eopt("10. Encrypted Normal")
	tools.eopt("11. Exit Program")
	tools.eline()

# Creates the baselayout
def create_baselayout():
	for b in variables.baselayout:
		subprocess.call(["mkdir", "-p", b])

# Ask the user if they want to use their current kernel, or another one
def do_kernel():
	global kernel
	global modules
	global lmodules
	global initrd

	if not kernel:
		currentKernel = subprocess.check_output(["uname", "-r"],
			universal_newlines=True).strip()
		eline()

		x = "Do you want to use the current kernel: " + currentKernel + \
			" [Y/n]: "

		choice = eqst(x)
		eline()

		if choice == 'y' or choice == 'Y' or choice == '':
			kernel = currentKernel
		elif choice == 'n' or choice == 'N':
			kernel = eqst("Please enter the kernel name: ")
			eline()

			if kernel == "":
				die("You didn't enter a kernel. Exiting...")
		else:
			die("Invalid Option. Exiting.")

	# Set modules path to correct location and sets kernel name for initramfs
	modules = "/lib/modules/" + kernel + "/"
	lmodules = variables.temp + "/" + modules
	initrd = "initrd-" + kernel

	# Check modules directory
	check_mods_dir()

# Check to make sure the kernel modules directory exists
def check_mods_dir():
	global modules

	einfo("Checking to see if " + modules + " exists...")

	if not os.path.exists(modules):
		die("Modules directory doesn't exist.")

# Make sure that the arch is x86_64
def get_arch():
	if variables.arch != "x86_64":
		die("Your architecture isn't supported. Exiting.")

# Checks to see if the preliminary binaries exist
def check_prelim_binaries():
	einfo("Checking preliminary binaries...")

	# If the required binaries don't exist, then exit
	for x in variables.prel_bin:
		if not os.path.isfile(x):
			err_bin_dexi(x)

# Compresses the kernel modules and generates modprobe table
def do_modules():
	einfo("Compressing kernel modules...")

	cmd = "find " + lmodules + " -name " + "*.ko"
	cap = os.popen(cmd)

	for x in cap:
		cmd = "gzip -9 " + x.strip()
		subprocess.call(cmd, shell=True)

	cap.close()
	
	einfo("Generating modprobe information...")

	# Copy modules.order and modules.builtin just so depmod
	# doesn't spit out warnings. -_-
	ecopy(modules + "/modules.order")
	ecopy(modules + "/modules.builtin")

	result = subprocess.call(["depmod", "-b", variables.temp, kernel])

	if result != 0:
		die("Either you don't have depmod, or another problem occured")

# Create the required symlinks to it
def create_links():
	einfo("Creating symlinks...")

	# Needs to be from this directory so that the links are relative
	os.chdir(variables.lbin)

	# Create busybox links
	cmd = "chroot " + variables.temp + \
	" /bin/busybox sh -c \"cd /bin && /bin/busybox --install -s .\""
	
	subprocess.call(cmd, shell=True)

	# Create 'sh' symlink to 'bash'
	os.remove(variables.temp + "/bin/sh")
	os.symlink("bash", "sh")
	
	# Switch to the kmod directory, delete the corresponding busybox
	# symlink and create the symlinks pointing to kmod
	if os.path.isfile(variables.lsbin + "/kmod"):
		os.chdir(variables.lsbin)
	elif os.path.isfile(variables.lbin + "/kmod"):
		os.chdir(variables.lbin)

	for target in base.kmod_links:
		os.remove(variables.temp + "/bin/" + target)
		os.symlink("kmod", target)

	# If 'lvm.static' exists, then make a 'lvm' symlink to it
	if os.path.isfile(variables.lsbin + "/lvm.static"):
		os.symlink("lvm.static", "lvm")

# This functions does any last minute steps like copying zfs.conf,
# giving init execute permissions, setting up symlinks, etc
def last_steps():
	einfo("Performing finishing steps...")

	# Create empty mtab file
	subprocess.call(["touch", variables.temp + "/etc/mtab"])

	if not os.path.isfile(variables.temp + "/etc/mtab"):
		die("Error creating the mtab file. Exiting.")

	# Set library symlinks
	if os.path.isdir(variables.temp + "/usr/lib") and \
	   os.path.isdir(variables.temp + "/lib64"):
		pcmd = "find /usr/lib -iname \"*.so.*\" -exec ln -s \"{}\" /lib64 \;"

		cmd = "chroot " + variables.temp + " /bin/busybox sh -c \"" + \
		pcmd + "\""
		
		subprocess.call(cmd, shell=True)

	if os.path.isdir(variables.temp + "/usr/lib32") and \
	   os.path.isdir(variables.temp + "/lib32"):
		pcmd = "find /usr/lib32 -iname \"*.so.*\" -exec ln -s \"{}\" /lib32 \;"
		
		cmd = "chroot " + variables.temp + " /bin/busybox sh -c \"" + \
		pcmd + "\""
		
		subprocess.call(cmd, shell=True)

	if os.path.isdir(variables.temp + "/usr/lib64") and \
	   os.path.isdir(variables.temp + "/lib64"):
		pcmd = "find /usr/lib64 -iname \"*.so.*\" -exec ln -s \"{}\" /lib64 \;"
		
		cmd = "chroot " + variables.temp + " /bin/busybox sh -c \"" + \
		pcmd + "\""
		
		subprocess.call(cmd, shell=True)

	# Copy init functions
	shutil.copytree(variables.phome + "/files/libs/", variables.temp + "/libs")

	# Copy the init script
	shutil.copy(variables.phome + "/files/init", variables.temp)

	# Give execute permissions to the script
	subprocess.call(["chmod", "u+x", variables.temp + "/init"])

	if not os.path.isfile(variables.temp + "/init"):
		die("Error creating the init file. Exiting.")

	# Fix 'poweroff, reboot' commands
	subprocess.call("sed -i \"71a alias reboot='reboot -f' \" " +
		variables.temp + "/etc/bash/bashrc", shell=True)

	subprocess.call("sed -i \"71a alias poweroff='poweroff -f' \" " +
		variables.temp + "/etc/bash/bashrc", shell=True)

	# Sets initramfs script version number
	subprocess.call(["sed", "-i", "-e", "19s/0/" + variables.version +
		"/", variables.temp + "/init"])

	# Fix EDITOR/PAGER
	subprocess.call(["sed", "-i", "-e", "12s:/bin/nano:/bin/vi:",
		variables.temp + "/etc/profile"])

	subprocess.call(["sed", "-i", "-e", "13s:/usr/bin/less:/bin/less:",
		variables.temp + "/etc/profile"])

	# Any last substitutions or additions/modifications should be done here
	if zfs.use == "1":
		# Enable ZFS in the init if ZFS is being used
		subprocess.call(["sed", "-i", "-e", "13s/0/1/",
			variables.temp + "/init"])

		# Copy the /etc/modprobe.d/zfs.conf file if it exists
		if os.path.isfile("/etc/modprobe.d/zfs.conf"):
			shutil.copy("/etc/modprobe.d/zfs.conf",
				variables.temp + "/etc/modprobe.d")

	# Enable RAID in the init if RAID is being used
	if raid.use == "1":
		subprocess.call(["sed", "-i", "-e", "14s/0/1/",
			variables.temp + "/init"])

	# Enable LVM in the init if LVM is being used
	if lvm.use == "1":
		subprocess.call(["sed", "-i", "-e", "15s/0/1/",
			variables.temp + "/init"])

	# Enable LUKS in the init if LUKS is being used
	if luks.use == "1":
		subprocess.call(["sed", "-i", "-e", "16s/0/1/",
			variables.temp + "/init"])
   
	# Enable ADDON in the init and add our modules to the initramfs
	# if addon is being used
	if addon.use == "1":
		subprocess.call(["sed", "-i", "-e", "17s/0/1/", 
			variables.temp + "/init"])
		subprocess.call(["sed", "-i", "-e", "20s/\"\"/\"" + 
		" ".join(addon.modules) + "\"/", variables.temp + "/libs/common.sh"])

# Create the solution
def create():
	einfo("Creating the initramfs...")

	# The find command must use the `find .` and not `find ${T}`
	# because if not, then the initramfs layout will be prefixed with
	# the ${T} path.
	os.chdir(variables.temp)

	subprocess.call(["find . -print0 | cpio -o --null --format=newc | \
		gzip -9 > " +  variables.home + "/" + initrd], shell=True)

	if not os.path.isfile(variables.home + "/" + initrd):
		die("Error creating the initramfs. Exiting.")

# Clean up and exit after a successful build
def clean_exit():
	eline(); einfo("[ Complete ]"); eline()
	clean()

	einfo("Please copy the " + initrd + " to your /boot directory")
	quit()

# Intelligently copies the file into the initramfs
def ecopy(f):
	# NOTE: shutil.copy will copy the program a symlink points
	# to but not the link..

	# Check to see if a file with this name exists before copying,
	# if it exists, delete it, then copy. If a directory, create the directory
	# before copying.
	p = variables.temp + "/" + f

	if os.path.exists(p):
		if os.path.isfile(p):
			os.remove(p)
			shutil.copy(f, p)
	else:
		if os.path.isdir(f):
			os.makedirs(p)
		elif os.path.isfile(f):
			# Make sure that the directory that this file wants to be in
			# exists, if not then create it.
			if os.path.isdir(os.path.dirname(p)):
				shutil.copy(f, p)
			else:
				os.makedirs(os.path.dirname(p))
				shutil.copy(f, p)

# Finds the path to a program on the system
def find_prog(prog):
	p1 = subprocess.Popen(
	["whereis", prog],
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
		die("Unable to find: " + prog)
		quit(1)

