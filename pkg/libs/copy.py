#!/usr/bin/env python

# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

from .common import *
from subprocess import PIPE, CalledProcessError

binset = set()     # List of binaries (That will be 'ldd'ed later)
modset = set()     # List of modules that will be compressed

# Checks to see if the binaries exist
def check_binaries():
        einfo("Checking binaries...")

        # Check base binaries (all initramfs have these)
        for x in base.base_bins:
                if not os.path.isfile(x):
                        err_bin_dexi(x)

        # If using ZFS, check the zfs binaries
        if zfs.use_zfs == "1":
                eflag("Using ZFS")

                for x in zfs.zfs_bins:
                        if not os.path.isfile(x):
                                err_bin_dexi(x)

        # If using LVM, check the lvm binaries
        if lvm.use_lvm == "1":
                eflag("Using LVM")

                if not lvm.lvm_bins:
                        err_bin_dexi("lvm", "sys-fs/lvm2")

        # If using RAID, check the raid binaries
        if raid.use_raid == "1":
                eflag("Using RAID")

                for x in raid.raid_bins:
                        if not os.path.isfile(x):
                                err_bin_dexi(x)

        # If using LUKS, check the luks binaries
        if luks.use_luks == "1":
                eflag("Using LUKS")

                for x in luks.luks_bins:
                        if not os.path.isfile(x):
                                err_bin_dexi(x)

                for x in luks.gpg_bins:
                        if not os.path.isfile(x):
                                err_bin_dexi(x)

# Installs the packages
def install():
        if base.use_base == "1":
            for pack in base.base_packs:
                emerge(pack)

        if zfs.use_zfs == "1":
            for pack in zfs.zfs_packs:
                emerge(pack)

        if lvm.use_lvm == "1":
            for pack in lvm.lvm_packs:
                emerge(pack)

        if raid.use_raid == "1":
            for pack in raid.raid_packs:
                emerge(pack)

        if luks.use_luks == "1":
            for pack in luks.luks_packs:
                emerge(pack)

# Filters and installs a package into the initramfs
def emerge(x):
    eopt("Emerging " + x + "...")

    global binset; global modset

    # Make the filter set
    filtered = set()

    remove = ""

    if x in filter.packages.keys():
        # Break up the directories written in the dictionary so we can recreate
        # a string with proper formatting (pipes separating the directories) for grep
        sl = filter.packages[x].split()

        for z in sl:
            if not remove:
                remove = z
            else:
                remove = remove + "|" + z

        # popen here and grep away the stuff we don't want, then add the
        # remaining to a set and that's what we will use during emerge
        cmd = "equery -C f " + x + " | grep -Ev \"" + remove + "\""
        cap = os.popen(cmd)

        for result in cap.readlines():
            # Add the file to our current install batch
            filtered.add(result.strip())

            # If the application is a binary, add it to our binary set
            try:
                lcmd = check_output("file " + result.strip() + " | grep \"linked\"",
                universal_newlines=True, shell=True).strip()
                binset.add(result)
            except CalledProcessError:
                # Else if the application is a module, add it to our module set
                try:
                    lcmd = check_output("file " + result.strip() + " | grep \"/lib/modules\" \
                    | grep \"LSB relocatable\"", universal_newlines=True, shell=True).strip()
                    modset.add(result)
                except CalledProcessError:
                    pass

        for f in filtered:
            ecopy(f)

    else:
        cmd = "equery -C f " + x
        cap = os.popen(cmd)

        for i in cap.readlines():
            filtered.add(i.strip())

            # If the application is a binary, add it to our binary set
            try:
                lcmd = check_output("file " + i.strip() + " | grep \"linked\"",
                universal_newlines=True, shell=True).strip()
                binset.add(i)
            except CalledProcessError:
                # Else if the application is a module, add it to our module set
                try:
                    lcmd = check_output("file " + i.strip() + " | grep \"/lib/modules\" \
                    | grep \"LSB relocatable\"", universal_newlines=True, shell=True).strip()
                    modset.add(i)
                except CalledProcessError:
                    pass

        for f in filtered:
            ecopy(f)

# Intelligently copies the file into the initramfs
def ecopy(f):
        # NOTE: shutil.copy will copy the program a symlink points to but not the link..

        # Check to see if a file with this name exists before copying,
        # if it exists, delete it, then copy. If a directory, create the directory
        # before copying.
        p = temp + "/" + f

        if os.path.exists(p):
            if os.path.isfile(p):
                os.remove(p)
                shutil.copy(f, p)
        else:
            if os.path.isdir(f):
                os.makedirs(p)
            elif os.path.isfile(f):
                # Make sure that the directory that this file wants to be in exists,
                # if not then create it.
                if os.path.isdir(os.path.dirname(p)):
                    shutil.copy(f, p)
                else:
                    os.makedirs(os.path.dirname(p))
                    shutil.copy(f, p)

# Copy modules and their dependencies
def copy_modules():
        einfo("Copying modules...")

        global modset; moddeps = set()

        if addon.use_addon == "1":
                # Build the list of module dependencies

                # Checks to see if all the modules in the list exist
                for x in addon.addon_mods:
                        try:
                            cmd = "find " + modules + " -iname \"" + x + ".ko\""
                            result = check_output(cmd, universal_newlines=True, shell=True).strip()
                            modset.add(result)
                        except CalledProcessError:
                                err_mod_dexi(x)

                for x in modset:
                    # Get only the name of the module
                    match = re.search('(?<=/)\w+.ko', x)

                    if match:
                        sx = match.group().split(".")[0]

                        cmd = "modprobe -S " + kernel + " --show-depends " + sx + " | awk -F ' ' '{print $2}'"
                        cap = os.popen(cmd)

                        for i in cap.readlines():
                                moddeps.add(i.strip())

        if moddeps:
                # Making sure that the dependencies are up to date
                call(["depmod", kernel])

                if addon.use_addon == "1":
                        for x in moddeps:
                                ecopy(x)

                # Compress the modules and update dependencies
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

        # Copy all the dependencies of the binary files into the initramfs
        for x in bindeps:
            ecopy(x)
