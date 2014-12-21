# Copyright 2012-2014 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import sys
import random

# Application Info
name = "Bliss Initramfs"
author = "Jonathan Vasquez"
email = "jvasquez1011@gmail.com"
contact = author + " <" + email + ">"
version = "6.0.0"
license = "Apache License 2.0"

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
    temp + "/root",
    temp + "/run"
]
