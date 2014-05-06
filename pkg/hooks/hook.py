# Copyright 2012-2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pkg.libs.toolkit import Toolkit as tools

class Hook:
	use = 0

	files = []

	# Enables the use value
	@classmethod
	def enable_use(cls):
		cls.use = 1

	# Disables the use value
	@classmethod
	def disable_use(cls):
		cls.use = 0

	# Gets the use value
	@classmethod
	def get_use(cls):
		return cls.use

	# Adds a file to the list
	@classmethod
	def add_to_files(cls, afile):
		cls.files.append(afile)

	# Deletes a file from the list
	@classmethod
	def remove_from_files(cls, afile):
		try:
			cls.files.remove(afile)
		except ValueError:
			tools.die("The file \"" + afile + "\" was not found on the list!")

	# Prints the files in the list
	@classmethod
	def print_files(cls):
		for i in cls.files:
			print("File: " + i)

	# Returns the list
	@classmethod
	def get_files(cls):
		return cls.files
