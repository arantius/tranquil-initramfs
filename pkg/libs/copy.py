#!/usr/bin/env python

# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

from .common import *
from subprocess import PIPE, CalledProcessError, Popen

packslist = set()
filedeps = set()

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

# Builds the file list for the base_packs
def install_list():
        #einfo("Installing packs...")

        if base.use_base == "1":
            for pack in base.base_packs:
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


def emerge(x):
        eopt("Emerging " + x + "...")

        global packslist
        locallist = set()

        #eflag("Gathering required files...")

        cmd = "equery -C f " + x
        #grep -v \"/usr/include\""

        cap = os.popen(cmd)

        for i in cap.readlines():
            #print("File: " + i.strip())
            packslist.add(i.strip())
            locallist.add(i.strip())

        #eflag("Installing files...")

        for pack in locallist:
            # NOTE: shutil.copy will copy the program a symlink points to 
            # but not the link..

            # Check to see if a file with this name exists before copying,
            # if it exists, delete it, then copy. If a directory, create the directory
            # before copying.
            p = temp + "/" + pack

            if os.path.exists(p):
                if os.path.isfile(p):
                    os.remove(p)
                    shutil.copy(pack, p)
            else:
                if os.path.isdir(pack):
                    os.makedirs(p)
                elif os.path.isfile(pack):
                    # Make sure that the directory that this file wants to be in exists,
                    # if not then create it.
                    if os.path.isdir(os.path.dirname(p)):
                        shutil.copy(pack, p)
                    else:
                        os.makedirs(os.path.dirname(p))
                        shutil.copy(pack, p)

# Copy the required binary files into the initramfs
def copy_binaries():
        einfo("Copying binaries...")

        # Copy base binaries (all initramfs have these)
        for x in base.base_bins:
                if re.search('(?<=/)busybox', x):
                        shutil.copy(x, lbin)
                else:
                        ecp("--parents", x, temp)

        if zfs.use_zfs == "1":
                for x in zfs.zfs_bins:
                        ecp("--parents", x, temp)

        if lvm.use_lvm == "1":
                for x in lvm.lvm_bins:
                        if re.search('(?<=/)lvm.static', x):
                                ecp("--parents", x, temp)
                                os.rename(temp + x, temp + os.path.dirname(x) + "/lvm")
                        else:
                                ecp("--parents", x, temp)

        if raid.use_raid == "1":
                for x in raid.raid_bins:
                        ecp("--parents", x, temp)

        if luks.use_luks == "1":
                for x in luks.luks_bins:
                        ecp("--parents", x, temp)

                for x in luks.gpg_bins:
                        ecp("--parents", x, temp)

# Copy modules and their dependencies
def copy_modules():
        einfo("Copying modules...")

        global moddeps; moddeps = set()

        if addon.use_addon == "1":
                # Checks to see if all the modules in the list exist
                for x in addon.addon_mods:
                        cmd = "find " + modules + " -iname " + x + " | grep " + x
                        result = call(cmd, shell=True, stdout=PIPE)

                        if result == 1:
                                err_mod_dexi(x)

                # Build the list of module dependencies
                for x in addon.addon_mods:
                        cmd = "modprobe -S " + kernel + " --show-depends " + x + " | awk -F ' ' '{print $2}'"
                        cap = os.popen(cmd)

                        for i in cap.readlines():
                                moddeps.add(i.strip())

        if moddeps:
                # Making sure that the dependencies are up to date
                call(["depmod", kernel])

                if addon.use_addon == "1":
                        for x in moddeps:
                                ecp("--parents", "-r", x, temp)

                # Compress the modules and update dependencies
                do_modules()
        else:
                # No modules will be used. Deleting the empty tree in the temporary directory
                if os.path.exists(lmodules):
                        shutil.rmtree(temp + "/lib")

# Copy any other files that need to be copied
def copy_other():
        einfo("Copying other files...")

        if base.use_base == "1":
                os.makedirs(temp + "/etc/bash")

                shutil.copy(plugins + "/singles/bashrc", temp + "/etc/bash/")
                shutil.copy(plugins + "/singles/man_db.conf", temp + "/etc/man_db.conf")
                shutil.copy("/etc/DIR_COLORS", temp + "/etc/")

        if luks.use_luks == "1":
                for x in luks.gpg_files:
                        ecp("--parents", x, temp)

        if lvm.use_lvm == "1":
                for x in lvm.lvm_files:
                        ecp("--parents", x, temp)

# Gets dependency list for parameter
def get_dlist(prog):
        global filedeps

        # Check to see if this is an executable file (We don't want to ldd
        # files that are directories or other stuff)
        cmd = "file " + prog + " | grep \"linked\""
        cap = os.popen(cmd)

        # There's probably a better way to check if the output of popen was null
        for i in cap.readlines():
            if i:
                #print("Program: " + i)

                cmd = "ldd " + prog + " | awk -F '=>' '{print $2}' | sed '/^ *$/d' | awk -F '(' '{print $1}'"
                cap = os.popen(cmd)

                for j in cap.readlines():
                        filedeps.add(j.strip())
        
def copy_deps():
        einfo("Copying library dependencies...")

        global filedeps
        global packslist

        # Get the interpreter name that is on this system
        r = check_output("ls " + lib64 + "/ld-linux-x86-64.so*", universal_newlines=True, shell=True).strip()

        # Add intepreter to deps since everything will depend on it
        filedeps.add(r)

        for pack in packslist:
            get_dlist(pack)

        #for x in filedeps:
            #print("Dependency: " + x)

        #print("There are: " + str(len(filedeps)) + " dependencies.")

        #for x in base.base_bins:
        #       get_dlist(x)

        #if zfs.use_zfs == "1":
        #       for x in zfs.zfs_bins:
        #               get_dlist(x)

        #if luks.use_luks == "1":
        #       for x in luks.luks_bins:
        #               get_dlist(x)

        #       for x in luks.gpg_bins:
        #               get_dlist(x)
        
        # Copy all the dependencies of the binary files into the initramfs
        for x in filedeps:
               ecp("--parents", x, temp)
