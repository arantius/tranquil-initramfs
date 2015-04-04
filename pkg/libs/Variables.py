# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the Simplified BSD License which can be found in the LICENSE file.

import os
import subprocess
import sys
import random

# Application Info
name = "Bliss Initramfs"
author = "Jonathan Vasquez"
email = "jvasquez1011@gmail.com"
contact = author + " <" + email + ">"
version = "6.2.0"
license = "Simplified BSD License"

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
useZfsLine = "7"
useLuksLine = "8"
useAddonLine = "9"
useUdevLine = "10"
initrdVersionLine = "12"
addonModulesLine = "35"
