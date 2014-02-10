#!/usr/bin/env python

# Copyright (C) 2012-2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

from .common import *
from subprocess import CalledProcessError

binset = set()     # List of binaries (That will be 'ldd'ed later)
modset = set()     # List of modules that will be compressed

# Checks to see if the binaries exist, if not then emerge
def check_binaries():
        einfo("Checking required files...")

        # Check required base files
        for file in base.files:
            if not os.path.exists(file):
                err_bin_dexi(file)

        # Check required zfs files
        if zfs.use == "1":
            eflag("Using ZFS")
            if not os.path.exists(file):
                err_bin_dexi(file)

        # Check required lvm files
        if lvm.use == "1":
            eflag("Using LVM")
            for file in lvm.files:
                if not os.path.exists(file):
                    err_bin_dexi(file)

        # Check required raid files
        if raid.use == "1":
            eflag("Using RAID")
            for file in raid.files:
                if not os.path.exists(file):
                    err_bin_dexi(file)

        # Check required luks files
        if luks.use == "1":
            eflag("Using LUKS")
            for file in luks.files:
                if not os.path.exists(file):
                    err_bin_dexi(file)

# Installs the packages
def install():
        einfo("Copying required files...")

        for file in base.files:
            emerge(file)

        if zfs.use == "1":
            for file in zfs.files:
                emerge(file)

        if lvm.use == "1":
            for file in lvm.files:
                emerge(file)
        
        if raid.use == "1":
            for file in raid.files:
                emerge(file)

        if luks.use == "1":
            for file in luks.files:
                emerge(file)

# Filters and installs a package into the initramfs
def emerge(file):
    global binset; global modset

    # If the application is a binary, add it to our binary set
    try:
        lcmd = check_output("file " + file.strip() + " | grep \"linked\"",
        universal_newlines=True, shell=True).strip()
        binset.add(file)
    except CalledProcessError:
        pass

    # Copy the file into the initramfs
    ecopy(file)

# Copy modules and their dependencies
def copy_modules():
        einfo("Copying modules...")

        global modset; moddeps = set()

        # Build the list of module dependencies
        if addon.use == "1":
                # Checks to see if all the modules in the list exist
                for x in addon.modules:
                        try:
                            cmd = "find " + modules + " -iname \"" + x + ".ko\" | grep " + x + ".ko"
                            result = check_output(cmd, universal_newlines=True, shell=True).strip()
                            modset.add(result)
                        except CalledProcessError:
                                err_mod_dexi(x)

        # If a kernel has been set, try to update the module dependencies
        # database before searching it
        if kernel:
            result = call(["depmod", kernel])

            if result == 1:
                die("Error updating module dependency database!")

        # Get the dependencies for all the modules in our set
        for x in modset:
            # Get only the name of the module
            match = re.search('(?<=/)\w+.ko', x)

            if match:
                sx = match.group().split(".")[0]
                
                cmd = "modprobe -S " + kernel + " --show-depends " + sx + " | awk -F ' ' '{print $2}'"
                cap = os.popen(cmd)

                for i in cap.readlines():
                        moddeps.add(i.strip())

                cap.close()

        # Copy the modules/dependencies
        if moddeps:
                for x in moddeps: ecopy(x)

                # Compress the modules and update module dependency database
                # inside the initramfs
                do_modules()

# Gets the library dependencies for all our binaries and copies them
# into our initramfs.
def copy_deps():
        einfo("Copying library dependencies...")

        bindeps = set()

        # Get the interpreter name that is on this system
        r = check_output("ls " + lib64 + "/ld-linux-x86-64.so*", universal_newlines=True, shell=True).strip()

        # Add intepreter to deps since everything will depend on it
        bindeps.add(r)

        # Get the dependencies for the binaries we've collected and add them to
        # our bindeps set. These will all be copied into the initramfs later.
        for b in binset:
            cmd = "ldd " + b.strip() + " | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}'"
            cap = os.popen(cmd)

            for j in cap.readlines():
                    bindeps.add(j.strip())

            cap.close()

        # Copy all the dependencies of the binary files into the initramfs
        for x in bindeps:
            ecopy(x)
