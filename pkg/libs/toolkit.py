#!/usr/bin/env python

"""
Copyright (C) 2012-2014 Jonathan Vasquez <fearedbliss@funtoo.org>

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
"""

import subprocess
import os
import shutil

class Toolkit(object):
	def find_prog(self, prog):
		"""
		Finds the path to a program on the system
		"""

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
			self.die("Unable to find: " + prog)
			quit(1)

	# Check to see if the temporary directory exists, if it does,
	# delete it for a fresh start
	def clean(self):
		# Go back to the original working directory so that we are
		# completely sure that there will be no inteference cleaning up.
		os.chdir(var.home)

		if os.path.exists(var.temp):
			shutil.rmtree(var.temp)

			if os.path.exists(var.temp):
				self.ewarn("Failed to delete the " + var.temp + \
				" directory. Exiting.")
				quit()

	####### Message Functions #######

	# Used for displaying information
	def einfo(self, x):
		subprocess.call(["echo", "-e", "\e[1;32m>>>\e[0;m " + x ])

	# Used for input (questions)
	def eqst(self, x):
		return input(x)

	# Used for warnings
	def ewarn(self, x):
		subprocess.call(["echo", "-e", "\e[1;33m>>>\e[0;m " + x])

	# Used for flags (aka using zfs, luks, etc)
	def eflag(self, x):
		subprocess.call(["echo", "-e", "\e[1;34m>>>\e[0;m " + x])

	# Used for options
	def eopt(self, x):
		subprocess.call(["echo", "-e", "\e[1;36m>>>\e[0;m " + x])

	# Used for errors
	def die(self, x):
		self.eline()
		subprocess.call(["echo", "-e", "\e[1;31m>>>\e[0;m " + x])
		self.eline()
		self.clean()
		quit(1)

	# Prints empty line
	def eline(self):
		print("")

	# Error Function: Binary doesn't exist
	def err_bin_dexi(self, x):
		die("Binary: " + x + " doesn't exist. Exiting.")

	# Error Function: Module doesn't exist
	def err_mod_dexi(self, x):
		die("Module: " + x + " doesn't exist. Exiting.")

	# Message for displaying the starting generating event
	def print_start(self):
		eline()
		einfo("[ Starting ]")
		eline()
