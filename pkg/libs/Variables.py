# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>.

import os
import subprocess
import sys
import random

# Application Info
name = "Bliss Initramfs"
author = "Jonathan Vasquez"
email = "jvasquez1011@gmail.com"
contact = author + " <" + email + ">"
version = "6.1.1"
license = "GPLv2"

# Locations
home = os.getcwd()

# Kernel and Menu Choice
kernel = ""
modules = ""
lmodules = ""
initrd = "initrd"
choice = ""

rstring = str(random.randint(100000000,999999999))

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

# Firmware directory
firmwareDirectory = "/lib/firmware/"

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
    temp + "/root",
    temp + "/run"
]

# Line numbers in the 'init' script where sed will substitute its values in
useZfsLine = "18"
useLuksLine = "19"
useAddonLine = "20"
useUdevLine = "21"
initrdVersionLine = "23"
addonModulesLine = "46"
