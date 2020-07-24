# Copyright (C) 2012-2020 Jonathan Vasquez <jon@xyinn.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pathlib
import subprocess
import sys
import random

# Application Info
name = "Tranquil Initramfs"
version = "v1"
license = "Apache License 2.0"

# Locations
home = os.getcwd()
config_default_file = pathlib.Path(os.path.dirname(__file__)) / '../../config-default.ini'
config_file = pathlib.Path(os.path.dirname(__file__)) / '../../config.ini'

# Kernel and Menu Choice
kernel = ""
modules = ""
lmodules = ""
initrd = "initrd"
features = ""

rstring = str(random.randint(100000000, 999999999))

# Temporary directory will now be in 'home' rather than
# in /tmp since people may have mounted their /tmp with 'noexec'
# which would cause tranquil-initramfs to fail to execute any binaries
# in the temp dir.
temp = home + "/bi-" + rstring

# Directory of Program
phome = os.path.dirname(os.path.realpath(sys.argv[0]))

# Files Directory
files_dir = phome + "/files"

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
prel_bin = ["/bin/cpio", "/sbin/depmod"]

# Firmware directory
firmwareDirectory = "/lib/firmware/"

# Layout of the initramfs
baselayout = [
    temp + "/etc",
    temp + "/etc/bash",
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
    temp + "/run",
]
