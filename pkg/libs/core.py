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

class Core(object):
	"""
	Contains the core of the application
	"""

	def __init__(self, var, tools):
		self.var = var
		self.tools = tools
		self.base = Base()
		self.zfs = ZFS()
		self.lvm = LVM()
		self.raid = RAID()
		self.luks = LUKS()
		self.addon = Addon()

		self.choice = ""

	def print_header(self):
		""" Prints the header of the application """

		call(["echo", "-e", "\e[1;33m----------------------------------\e[0;m"])
		
		call(["echo", "-e", "\e[1;33m| " + self.var.name + " - v" +
		self.var.version + "\e[0;m"])

		call(["echo", "-e", "\e[1;33m| " + self.var.contact + "\e[0;m"])
		
		call(["echo", "-e", "\e[1;33m| Distributed under the " +
		self.var.license + "\e[0;m"])
		
		call(["echo", "-e", "\e[1;33m----------------------------------\e[0;m"])

	def print_menu(self):
		""" Prints the menu and accepts user choice """

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

	def print_options(self):
		"""
		Prints the available options
		"""

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

	def create_baselayout(self):
		"""
		Creates the base directory structure
		"""

		for b in self.var.baselayout:
			call(["mkdir", "-p", b])

	def do_kernel(self):
		"""
		Ask the user if they want to use their current kernel, or another one
		"""

		if not self.var.kernel:
			current_kernel = check_output(["uname", "-r"],
			                universal_newlines=True).strip()

			tools.eline()

			x = "Do you want to use the current kernel: " + \
			     current_kernel + " [Y/n]: "

			self.choice = tools.eqst(x)
			tools.eline()

			if self.choice == 'y' or self.choice == 'Y' or self.choice == '':
				self.var.kernel = current_kernel
			elif self.choice == 'n' or self.choice == 'N':
				self.var.kernel = tools.eqst("Please enter the kernel name: ")
				tools.eline()

				if self.var.kernel == "":
					tools.die("You didn't enter a kernel. Exiting...")
			else:
				tools.die("Invalid Option. Exiting.")

		# Set modules path to correct location and sets kernel name for initramfs
		self.var.modules = "/lib/modules/" + self.var.kernel + "/"
		self.var.lmodules = self.var.temp + "/" + self.var.modules
		self.var.initrd = "initrd-" + self.var.kernel

		# Check modules directory
		self.check_mods_dir()

	def check_mods_dir(self):
		"""
		Check to make sure the kernel modules directory exists
		"""

		tools.einfo("Checking to see if " + self.var.modules + " exists ...")

		if not os.path.exists(self.var.modules):
			tools.die("Modules directory doesn't exist.")

	def get_arch(self):
		"""
		Make sure that the arch is x86_64
		"""

		if self.var.arch != "x86_64":
			tools.die("Your architecture isn't supported. Exiting.")

	def check_prelim_binaries(self):
		"""
		Checks to see if the preliminary binaries exist
		"""

		tools.einfo("Checking preliminary binaries ...")

		# If the required binaries don't exist, then exit
		for x in self.var.prel_bin:
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
