# Copyright 2012-2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import re

from subprocess import call
from subprocess import check_output


from pkg.libs.toolkit import Toolkit as tools

import pkg.libs.variables as var

class Copy:
	def __init__(self, core):
		self.core = core



