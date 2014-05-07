# Copyright 2012-2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import subprocess
import sys
import random

# Application Info
name = "Bliss Initramfs Creator"
author = "Jonathan Vasquez"
email = "jvasquez1011@gmail.com"
contact = author + " <" + email + ">"
version = "5.0.0"
license = "MPL 2.0"

# Locations
home = os.getcwd()

# Kernel and Menu Choice
kernel = ""
modules = ""
lmodules = ""
initrd = "initrd"
choice = ""

rstring = str(random.randint(1000,2000)) + "-" + \
		  str(random.randint(2000,3000)) + "-" + \
		  str(random.randint(3000,4000)) + "-" + \
		  str(random.randint(4000,5000))

temp = "/tmp/" + rstring

# Temporary symlink created at home in order to easily find the random
# directory created. Gets deleted when program finishes successfully.
tlink = home + "/" + rstring

# Directory of Program
phome = os.path.dirname(os.path.realpath(sys.argv[0]))

# System Directories
bin = "/bin"
sbin = "/sbin"
lib = "/lib"
lib64 = "/lib64"
etc = "/etc"

# Paths in Temp (Local)
lbin = temp + bin
lsbin = temp + sbin
llib = temp + lib
llib64 = temp + lib64
letc = temp + etc

# CPU Architecture
arch = subprocess.check_output(["uname", "-m"], universal_newlines=True).strip()

# Preliminary binaries needed for the success of creating the initrd
# but that are not needed to be placed inside the initrd
prel_bin = [
	"/bin/cpio",
	"/sbin/depmod",
]

# Layout of the initramfs
baselayout = [
	temp + "/etc",
	temp + "/etc/zfs",
	temp + "/dev",
	temp + "/proc",
	temp + "/sys",
	temp + "/mnt",
	temp + "/mnt/root",
	temp + "/mnt/key",
	temp + "/lib",
	temp + "/lib/modules",
	temp + "/lib64",
	temp + "/bin",
	temp + "/sbin",
	temp + "/usr",
]
