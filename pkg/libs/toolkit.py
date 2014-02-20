#!/usr/bin/env python

"""
Copyright (C) 2012-2014 Jonathan Vasquez <fearedbliss@funtoo.org>

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""


from subprocess import call
from subprocess import check_output
from subprocess import Popen
from subprocess import PIPE

import os
import shutil
import sys

from pkg.libs.variables import Variables

class Toolkit(object):
	def __init__(self, var):
		self.var = var

	def welcome(self, core):
		"""
		Checks parameters and running user
		"""

		arguments = sys.argv[1:]

		# Let the user directly create an initramfs if no modules are needed
		if len(arguments) == 1:
			if arguments[0] != "1" and arguments[0] != "6":
				if not core.addon.modules:
					core.choice = arguments[0]
			else:
				self.die("You must pass a kernel parameter")

		# If there are two parameters then we will use them, else just ignore them
		elif len(arguments) == 2:
			core.choice = arguments[0]

			print("arg2: " + arguments[1])
			print("vark: " + var.kernel)
			var.kernel = arguments[1]
			print("vark: " + var.kernel)

		user = check_output(["whoami"], universal_newlines=True).strip()

		if user != "root":
			self.die("This program must be ran as root")

	def find_prog(self, prog):
		"""
		Finds the path to a program on the system
		"""

		p1 = Popen(["whereis", prog], stdout=PIPE, universal_newlines=True)

		p2 = Popen(["cut", "-d", " ", "-f", "2"], stdin=p1.stdout, stdout=PIPE,
		     universal_newlines=True)

		out = p2.stdout.readlines()

		if out:
			return out[0].strip()
		else:
			self.die("Unable to find: " + prog)
			quit(1)

	# Check to see if the temporary directory exists, if it does,
	# delete it for a fresh start
	def clean(self):
		# Go back to the original working directory so that we are
		# completely sure that there will be no inteference cleaning up.
		os.chdir(self.var.home)

		if os.path.exists(self.var.temp):
			shutil.rmtree(self.var.temp)

			if os.path.exists(self.var.temp):
				self.ewarn("Failed to delete the " + self.var.temp + \
				" directory. Exiting.")
				quit()

	####### Message Functions #######

	# Used for displaying information
	def einfo(self, x):
		call(["echo", "-e", "\e[1;32m>>>\e[0;m " + x ])

	# Used for input (questions)
	def eqst(self, x):
		return input(x)

	# Used for warnings
	def ewarn(self, x):
		call(["echo", "-e", "\e[1;33m>>>\e[0;m " + x])

	# Used for flags (aka using zfs, luks, etc)
	def eflag(self, x):
		call(["echo", "-e", "\e[1;34m>>>\e[0;m " + x])

	# Used for options
	def eopt(self, x):
		call(["echo", "-e", "\e[1;36m>>>\e[0;m " + x])

	# Used for errors
	def die(self, x):
		self.eline()
		call(["echo", "-e", "\e[1;31m>>>\e[0;m " + x])
		self.eline()
		self.clean()
		quit(1)

	# Prints empty line
	def eline(self):
		print("")

	# Error Function: Binary doesn't exist
	def err_bin_dexi(self, x):
		self.die("Binary: " + x + " doesn't exist. Exiting.")

	# Error Function: Module doesn't exist
	def err_mod_dexi(self, x):
		self.die("Module: " + x + " doesn't exist. Exiting.")

	# Message for displaying the starting generating event
	def print_start(self):
		self.eline()
		self.einfo("[ Starting ]")
		self.eline()
