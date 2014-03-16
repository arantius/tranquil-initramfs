#!/usr/bin/env python

"""
Copyright (C) 2012-2014 Jonathan Vasquez <fearedbliss@funtoo.org>

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import os
import shutil

from subprocess import call
from subprocess import check_output
from subprocess import PIPE
from subprocess import Popen

from pkg.libs.variables import Variables
from pkg.libs.toolkit import Toolkit

from pkg.hooks.base import Base
from pkg.hooks.zfs import ZFS
from pkg.hooks.lvm import LVM
from pkg.hooks.raid import RAID
from pkg.hooks.luks import LUKS
from pkg.hooks.addon import Addon

tools = Toolkit()
var = Variables()

class Core(object):
	"""
	Contains the core of the application
	"""

	def __init__(self):
		self.base = Base()
		self.zfs = ZFS()
		self.lvm = LVM()
		self.raid = RAID()
		self.luks = LUKS()
		self.addon = Addon()

		self.choice = ""
		self.kernel = ""
		self.modules = ""
		self.lmodules = ""
		self.initrd = "initrd"

	def print_header(self):
		""" Prints the header of the application """

		call(["echo", "-e", "\e[1;33m----------------------------------\e[0;m"])
		
		call(["echo", "-e", "\e[1;33m| " + var.name + " - v" +
		var.version + "\e[0;m"])

		call(["echo", "-e", "\e[1;33m| " + var.contact + "\e[0;m"])
		
		call(["echo", "-e", "\e[1;33m| Distributed under the " +
		var.license + "\e[0;m"])
		
		call(["echo", "-e", "\e[1;33m----------------------------------\e[0;m"])

	# Prints the menu and accepts user choice
	def print_menu(self):
		# If the user didn't pass an option through the command line,
		# then ask them which initramfs they would like to generate.
		if not self.choice:
			tools.einfo("Which initramfs would you like to generate:")
			self.print_options()
			self.choice = tools.eqst("Current choice [1]: ")

		# Enable the addons if the addon.mods is not empty
		if self.addon.modules:
			self.addon.use = "1"

		if self.choice == "1" or not self.choice:
			self.zfs.use = "1"
			self.addon.use = "1"
			self.addon.modules.append("zfs")
		elif self.choice == "2":
			self.lvm.use = "1"
		elif self.choice == "3":
			self.raid.use = "1"
		elif self.choice == "4":
			self.raid.use = "1"
			self.lvm.use = "1"
		elif self.choice == "5":
			pass
		elif self.choice == '6':
			self.luks.use = "1"
			self.zfs.use = "1"
			self.addon.use = "1"
			self.addon.modules.append("zfs")
		elif self.choice == "7":
			self.luks.use = "1"
			self.lvm.use = "1"
		elif self.choice == "8":
			self.luks.use = "1"
			self.raid.use = "1"
		elif self.choice == "9":
			self.luks.use = "1"
			self.raid.use = "1"
			self.lvm.use = "1"
		elif self.choice == "10":
			self.luks.use = "1"
		elif self.choice == '11':
			tools.ewarn("Exiting.")
			quit()
		else:
			tools.ewarn("Invalid Option. Exiting.")
			quit()

	# Prints the available options
	def print_options(self):
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

	# Creates the base directory structure
	def create_baselayout(self):
		for b in var.baselayout:
			call(["mkdir", "-p", b])

		# Create a symlink to this temporary directory at the home dir.
		# This will help us debug if anything (since the dirs are randomly
		# generated...)
		os.symlink(var.temp, var.tlink)

	# Ask the user if they want to use their current kernel, or another one
	def do_kernel(self):
		if not self.kernel:
			current_kernel = check_output(["uname", "-r"],
			                 universal_newlines=True).strip()

			tools.eline()

			x = "Do you want to use the current kernel: " + \
			     current_kernel + " [Y/n]: "

			self.choice = tools.eqst(x)
			tools.eline()

			if self.choice == 'y' or self.choice == 'Y' or self.choice == '':
				self.kernel = current_kernel
			elif self.choice == 'n' or self.choice == 'N':
				self.kernel = tools.eqst("Please enter the kernel name: ")
				tools.eline()

				if self.kernel == "":
					tools.die("You didn't enter a kernel. Exiting...")
			else:
				tools.die("Invalid Option. Exiting.")

		# Set modules path to correct location and
		# sets kernel name for initramfs
		self.modules = "/lib/modules/" + self.kernel + "/"
		self.lmodules = var.temp + "/" + self.modules
		self.initrd = "initrd-" + self.kernel

		# Check modules directory
		self.check_mods_dir()

	# Check to make sure the kernel modules directory exists
	def check_mods_dir(self):
		tools.einfo("Checking to see if " + self.modules + " exists ...")

		if not os.path.exists(self.modules):
			tools.die("Modules directory doesn't exist.")

	# Make sure that the arch is x86_64
	def get_arch(self):
		if var.arch != "x86_64":
			tools.die("Your architecture isn't supported. Exiting.")

	# Checks to see if the preliminary binaries exist
	def check_prelim_binaries(self):
		tools.einfo("Checking preliminary binaries ...")

		# If the required binaries don't exist, then exit
		for x in var.prel_bin:
			if not os.path.isfile(x):
				tools.err_bin_dexi(x)

	# Compresses the kernel modules and generates modprobe table
	def do_modules(self):
		tools.einfo("Compressing kernel modules ...")

		cmd = "find " + self.lmodules + " -name " + "*.ko"
		cap = os.popen(cmd)

		for x in cap:
			cmd = "gzip -9 " + x.strip()
			call(cmd, shell=True)

		cap.close()
		
		tools.einfo("Generating modprobe information ...")

		# Copy modules.order and modules.builtin just so depmod
		# doesn't spit out warnings. -_-
		tools.ecopy(self.modules + "/modules.order")
		tools.ecopy(self.modules + "/modules.builtin")

		result = call(["depmod", "-b", var.temp, self.kernel])

		if result != 0:
			tools.die("Either you don't have depmod, or " +
					  "another problem occured")

	# Create the required symlinks to it
	def create_links(self):
		tools.einfo("Creating symlinks ...")

		# Needs to be from this directory so that the links are relative
		os.chdir(var.lbin)

		# Create busybox links
		cmd = "chroot " + var.temp + \
		" /bin/busybox sh -c \"cd /bin && /bin/busybox --install -s .\""
		
		call(cmd, shell=True)

		# Create 'sh' symlink to 'bash'
		os.remove(var.temp + "/bin/sh")
		os.symlink("bash", "sh")
		
		# Switch to the kmod directory, delete the corresponding busybox
		# symlink and create the symlinks pointing to kmod
		if os.path.isfile(var.lsbin + "/kmod"):
			os.chdir(var.lsbin)
		elif os.path.isfile(var.lbin + "/kmod"):
			os.chdir(var.lbin)

		for target in self.base.kmod_links:
			os.remove(var.temp + "/bin/" + target)
			os.symlink("kmod", target)

		# If 'lvm.static' exists, then make a 'lvm' symlink to it
		if os.path.isfile(var.lsbin + "/lvm.static"):
			os.symlink("lvm.static", "lvm")

	# This functions does any last minute steps like copying zfs.conf,
	# giving init execute permissions, setting up symlinks, etc
	def last_steps(self):
		tools.einfo("Performing finishing steps ...")

		# Create mtab file
		call(["ln", "-sf", "/proc/mounts", var.temp + "/etc/mtab"])

		if not os.path.islink(var.temp + "/etc/mtab"):
			tools.die("Error creating the mtab file. Exiting.")

		# Set library symlinks
		if os.path.isdir(var.temp + "/usr/lib") and \
		   os.path.isdir(var.temp + "/lib64"):
			pcmd = "find /usr/lib -iname \"*.so.*\" " + \
			       "-exec ln -s \"{}\" /lib64 \;"

			cmd = "chroot " + var.temp + " /bin/busybox sh -c \"" + \
			pcmd + "\""
			
			call(cmd, shell=True)

		if os.path.isdir(var.temp + "/usr/lib32") and \
		   os.path.isdir(var.temp + "/lib32"):
			pcmd = "find /usr/lib32 -iname \"*.so.*\" " + \
			       "-exec ln -s \"{}\" /lib32 \;"
			
			cmd = "chroot " + var.temp + " /bin/busybox sh -c \"" + \
			pcmd + "\""
			
			call(cmd, shell=True)

		if os.path.isdir(var.temp + "/usr/lib64") and \
		   os.path.isdir(var.temp + "/lib64"):
			pcmd = "find /usr/lib64 -iname \"*.so.*\" " + \
			       "-exec ln -s \"{}\" /lib64 \;"
			
			cmd = "chroot " + var.temp + " /bin/busybox sh -c \"" + \
			pcmd + "\""
			
			call(cmd, shell=True)

		# Copy init functions
		shutil.copytree(var.phome + "/files/libs/", var.temp + "/libs")

		# Copy the init script
		shutil.copy(var.phome + "/files/init", var.temp)

		# Give execute permissions to the script
		call(["chmod", "u+x", var.temp + "/init"])

		if not os.path.isfile(var.temp + "/init"):
			tools.die("Error creating the init file. Exiting.")

		# Fix 'poweroff, reboot' commands
		call("sed -i \"71a alias reboot='reboot -f' \" " +
			var.temp + "/etc/bash/bashrc", shell=True)

		call("sed -i \"71a alias poweroff='poweroff -f' \" " +
			var.temp + "/etc/bash/bashrc", shell=True)

		# Sets initramfs script version number
		call(["sed", "-i", "-e", "19s/0/" + var.version +
			"/", var.temp + "/init"])

		# Fix EDITOR/PAGER
		call(["sed", "-i", "-e", "12s:/bin/nano:/bin/vi:",
			var.temp + "/etc/profile"])

		call(["sed", "-i", "-e", "13s:/usr/bin/less:/bin/less:",
			var.temp + "/etc/profile"])

		# Any last substitutions or additions/modifications should be done here
		if self.zfs.use == "1":
			# Enable ZFS in the init if ZFS is being used
			call(["sed", "-i", "-e", "13s/0/1/", var.temp + "/init"])

			# Copy the /etc/modprobe.d/zfs.conf file if it exists
			if os.path.isfile("/etc/modprobe.d/zfs.conf"):
				tools.ecopy("/etc/modprobe.d/zfs.conf")

			# Get the system's hostid now since it will default to 0
			# within the initramfs environment

			# source: https://bbs.archlinux.org/viewtopic.php?id=153868
			hostid = check_output(["hostid"], universal_newlines=True)

			cmd = "printf $(echo -n " + hostid.strip().upper() + " | " + \
			"sed 's/\(..\)\(..\)\(..\)\(..\)/\\\\x\\4\\\\x\\3\\\\x\\2\\\\x\\1/') " + \
			"> " + var.temp + "/etc/hostid"

			call(cmd, shell=True)
			
			# Copy zpool.cache into initramfs
			if os.path.isfile("/etc/zfs/zpool.cache"):
				tools.ecopy("/etc/zfs/zpool.cache")

		# Enable RAID in the init if RAID is being used
		if self.raid.use == "1":
			call(["sed", "-i", "-e", "14s/0/1/", var.temp + "/init"])

		# Enable LVM in the init if LVM is being used
		if self.lvm.use == "1":
			call(["sed", "-i", "-e", "15s/0/1/", var.temp + "/init"])

		# Enable LUKS in the init if LUKS is being used
		if self.luks.use == "1":
			call(["sed", "-i", "-e", "16s/0/1/", var.temp + "/init"])
	   
		# Enable ADDON in the init and add our modules to the initramfs
		# if addon is being used
		if self.addon.use == "1":
			call(["sed", "-i", "-e", "17s/0/1/", var.temp + "/init"])
			call(["sed", "-i", "-e", "20s/\"\"/\"" +
			" ".join(self.addon.modules) + "\"/", var.temp + "/libs/common.sh"])

	# Create the solution
	def create(self):
		tools.einfo("Creating the initramfs ...")

		# The find command must use the `find .` and not `find ${T}`
		# because if not, then the initramfs layout will be prefixed with
		# the ${T} path.
		os.chdir(var.temp)

		call(["find . -print0 | cpio -o --null --format=newc | \
			gzip -9 > " +  var.home + "/" + self.initrd], shell=True)

		if not os.path.isfile(var.home + "/" + self.initrd):
			tools.die("Error creating the initramfs. Exiting.")

	# Getters
	def get_kernel(self):
		return self.kernel

	def get_module(self):
		return self.module

	def get_initrd(self):
		return self.initrd
