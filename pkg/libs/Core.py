# Copyright 2012-2017 Jonathan Vasquez <jon@xyinn.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import shutil
import re

from subprocess import call
from subprocess import check_output
from subprocess import CalledProcessError

import pkg.libs.Variables as var

from pkg.libs.Tools import Tools
from pkg.hooks.Base import Base
from pkg.hooks.Luks import Luks
from pkg.hooks.Raid import Raid
from pkg.hooks.Lvm import Lvm
from pkg.hooks.Zfs import Zfs
from pkg.hooks.Addon import Addon
from pkg.hooks.Firmware import Firmware

# Contains the core of the application
class Core:
    # List of binaries (That will be 'ldd'ed later)
    _binset = set()

    # List of modules that will be compressed
    _modset = set()

    # Enable the 'base' hook since all initramfs will have this
    Base.Enable()

    @classmethod
    # Prints the menu and accepts user features
    def PrintMenuAndGetDesiredFeatures(cls):
        # If the user didn't pass their desired features through the command
        # line, then ask them which initramfs they would like to generate.
        if not var.features:
            print("Which initramfs features do you want? (Separated by a space):")
            Tools.PrintFeatures()
            var.features = Tools.Question("Features [1]: ")

            if var.features:
                var.features = cls.ConvertNumberedFeaturesToNamedList(var.features)
            else:
                var.features = "zfs"

            Tools.NewLine()
        else:
            var.features = var.features.split(",")

        # Enable the addons if the addon has files (modules) listed
        if Addon.GetFiles():
            Addon.Enable()

        for feature in var.features:
            if feature == "zfs":
                Zfs.Enable()
                Addon.Enable()
                Addon.AddFile("zfs")
            elif feature == "lvm":
                Lvm.Enable()
            elif feature == "raid":
                Raid.Enable()
            elif feature == "luks":
                Luks.Enable()
            # Just a base initramfs with no additional stuff
            # This can be used with other options though
            # (i.e you have your rootfs directly on top of LUKS)
            elif feature == "basic":
                pass
            else:
                Tools.Warn("Exiting.")
                quit(1)

    # Returns the name equivalent list of a numbered list of features
    @classmethod
    def ConvertNumberedFeaturesToNamedList(cls, numbered_feature_list):
        named_features = []

        for feature in numbered_feature_list.split(","):
            feature_as_string = Tools._features[int(feature)].lower()
            named_features.append(feature_as_string)

        return named_features

    # Creates the base directory structure
    @classmethod
    def CreateBaselayout(cls):
        Tools.Info("Creating temporary directory at " + var.temp + " ...")

        for dir in var.baselayout:
            call(["mkdir", "-p", dir])

    # Ask the user if they want to use their current kernel, or another one
    @classmethod
    def GetDesiredKernel(cls):
        if not var.kernel:
            current_kernel = check_output(["uname", "-r"], universal_newlines=True).strip()

            message = "Do you want to use the current kernel: " + current_kernel + " [Y/n]: "
            choice = Tools.Question(message)
            Tools.NewLine()

            if choice == 'y' or choice == 'Y' or not choice:
                var.kernel = current_kernel
            elif choice == 'n' or choice == 'N':
                var.kernel = Tools.Question("Please enter the kernel name: ")
                Tools.NewLine()

                if not var.kernel:
                    Tools.Fail("You didn't enter a kernel. Exiting...")
            else:
                Tools.Fail("Invalid Option. Exiting.")

        # Set modules path to correct location and sets kernel name for initramfs
        var.modules = "/lib/modules/" + var.kernel + "/"
        var.lmodules = var.temp + "/" + var.modules
        var.initrd = "initrd-" + var.kernel

        # Check modules directory
        cls.VerifyModulesDirectory()

    # Check to make sure the kernel modules directory exists
    @classmethod
    def VerifyModulesDirectory(cls):
        if not os.path.exists(var.modules):
            Tools.Fail("The modules directory for " + var.modules + " doesn't exist!")

    # Make sure that the arch is x86_64
    @classmethod
    def VerifySupportedArchitecture(cls):
        if var.arch != "x86_64":
            Tools.Fail("Your architecture isn't supported. Exiting.")

    # Checks to see if the preliminary binaries exist
    @classmethod
    def VerifyPreliminaryBinaries(cls):
        Tools.Info("Checking preliminary binaries ...")

        # If the required binaries don't exist, then exit
        for binary in var.prel_bin:
            if not os.path.isfile(binary):
                Tools.BinaryDoesntExist(binary)

    # Generates the modprobe information
    @classmethod
    def GenerateModprobeInfo(cls):
        Tools.Info("Generating modprobe information ...")

        # Copy modules.order and modules.builtin just so depmod doesn't spit out warnings. -_-
        Tools.Copy(var.modules + "/modules.order")
        Tools.Copy(var.modules + "/modules.builtin")

        result = call(["depmod", "-b", var.temp, var.kernel])

        if result != 0:
            Tools.Fail("Depmod was unable to refresh the dependency information for your initramfs!")

    # Copies the firmware files if necessary
    @classmethod
    def CopyFirmware(cls):
        if Firmware.IsEnabled():
            Tools.Info("Copying firmware...")

            if os.path.isdir("/lib/firmware/"):
                if Firmware.IsCopyAllEnabled():
                    shutil.copytree("/lib/firmware/", var.temp + "/lib/firmware/")
                else:
                    # Copy the firmware in the files list
                    if Firmware.GetFiles():
                        try:
                            for fw in Firmware.GetFiles():
                                Tools.Copy(fw, directoryPrefix=var.firmwareDirectory)
                        except FileNotFoundError:
                            Tools.Warn("An error occured while copying the following firmware: " + fw)
                    else:
                        Tools.Warn("No firmware files were found in the firmware list!")
            else:
                Tools.Fail("The /lib/firmware/ directory does not exist")

    # Create the required symlinks
    @classmethod
    def CreateLinks(cls):
        Tools.Info("Creating symlinks ...")

        # Needs to be from this directory so that the links are relative
        os.chdir(var.lbin)

        # Create busybox links
        cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "cd /bin && /bin/busybox --install -s ."'
        callResult = call(cmd, shell=True)

        if callResult != 0:
            Tools.Fail("Unable to create busybox links via chroot!")

        # Create 'sh' symlink to 'bash'
        os.remove(var.temp + "/bin/sh")
        os.symlink("bash", "sh")

        # Switch to the kmod directory, delete the corresponding busybox
        # symlink and create the symlinks pointing to kmod
        if os.path.isfile(var.lsbin + "/kmod"):
            os.chdir(var.lsbin)
        elif os.path.isfile(var.lbin + "/kmod"):
            os.chdir(var.lbin)

        for link in Base.GetKmodLinks():
            os.remove(var.temp + "/bin/" + link)
            os.symlink("kmod", link)

    # Creates symlinks from library files found in each /usr/lib## dir to the /lib[32/64] directories
    @classmethod
    def CreateLibraryLinks(cls):
        # Set library symlinks
        if os.path.isdir(var.temp + "/usr/lib") and os.path.isdir(var.temp + "/lib64"):
            pcmd = 'find /usr/lib -iname "*.so.*" -exec ln -s "{}" /lib64 \;'
            cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "' + pcmd + '"'
            call(cmd, shell=True)

        if os.path.isdir(var.temp + "/usr/lib32") and os.path.isdir(var.temp + "/lib32"):
            pcmd = 'find /usr/lib32 -iname "*.so.*" -exec ln -s "{}" /lib32 \;'
            cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "' + pcmd + '"'
            call(cmd, shell=True)

        if os.path.isdir(var.temp + "/usr/lib64") and os.path.isdir(var.temp + "/lib64"):
            pcmd = 'find /usr/lib64 -iname "*.so.*" -exec ln -s "{}" /lib64 \;'
            cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "' + pcmd + '"'
            call(cmd, shell=True)

    # Copies files that udev uses, like /etc/udev/*, /lib/udev/*, etc
    @classmethod
    def CopyUdevSupportFiles(cls):
        # Copy all of the udev files
        if os.path.isdir("/etc/udev/"):
            shutil.copytree("/etc/udev/", var.temp + "/etc/udev/")

        if os.path.isdir("/lib/udev/"):
            shutil.copytree("/lib/udev/", var.temp + "/lib/udev/")

        # Rename udevd and place in /sbin
        udev_path = Tools.GetUdevPath()
        systemd_dir = os.path.dirname(udev_path)

        if os.path.isfile(var.temp + udev_path) and udev_path != "/sbin/udevd":
            os.rename(var.temp + udev_path, var.temp + "/sbin/udevd")
            os.rmdir(var.temp + systemd_dir)

    # Dumps the current system's keymap
    @classmethod
    def DumpSystemKeymap(cls):
        pathToKeymap = var.temp + "/etc/keymap"
        result = call("dumpkeys > " + pathToKeymap, shell=True)

        if result != 0 or not os.path.isfile(pathToKeymap):
            Tools.Warn("There was an error dumping the system's current keymap. Ignoring.")

    # This functions does any last minute steps like copying zfs.conf,
    # giving init execute permissions, setting up symlinks, etc
    @classmethod
    def LastSteps(cls):
        Tools.Info("Performing finishing steps ...")

        # Create mtab file
        call(["touch", var.temp + "/etc/mtab"])

        if not os.path.isfile(var.temp + "/etc/mtab"):
            Tools.Fail("Error creating the mtab file. Exiting.")

        cls.CreateLibraryLinks()

        # Copy the init script
        Tools.SafeCopy(var.files_dir + "/init", var.temp)

        # Give execute permissions to the script
        cr = call(["chmod", "u+x", var.temp + "/init"])

        if cr != 0:
            Tools.Fail("Failed to give executive privileges to " + var.temp + "/init")

        # Copy the bash related files
        bash_files = [
            var.files_dir + "/bash/profile",
            var.files_dir + "/bash/DIR_COLORS"
        ]

        for bash_file in bash_files:
            Tools.SafeCopy(bash_file, var.temp + "/etc/")

        Tools.SafeCopy(var.files_dir + "/bash/bashrc", var.temp + "/etc/bash")

        # Sets initramfs script version number
        call(["sed", "-i", "-e", var.initrdVersionLine + "s/0/" + var.version + "/", var.temp + "/init"])

        # Copy all of the modprobe configurations
        if os.path.isdir("/etc/modprobe.d/"):
            shutil.copytree("/etc/modprobe.d/", var.temp + "/etc/modprobe.d/")

        cls.CopyUdevSupportFiles()
        cls.DumpSystemKeymap()

        # Any last substitutions or additions/modifications should be done here

        # Enable LUKS in the init if LUKS is being used
        if Luks.IsEnabled():
            Tools.ActivateTriggerInInit(var.useLuksLine)

            # Copy over our keyfile if the user activated it
            if Luks.IsKeyfileEnabled():
                Tools.Flag("Embedding our keyfile into the initramfs...")
                Tools.SafeCopy(Luks.GetKeyfilePath(), var.temp + "/etc", "keyfile")

            # Copy over our detached header if the user activated it
            if Luks.IsDetachedHeaderEnabled():
                Tools.Flag("Embedding our detached header into the initramfs...")
                Tools.SafeCopy(Luks.GetDetachedHeaderPath(), var.temp + "/etc", "header")

        # Enable RAID in the init if RAID is being used
        if Raid.IsEnabled():
            Tools.ActivateTriggerInInit(var.useRaidLine)

            # Make sure to copy the mdadm.conf from our current system.
            # If not, the kernel autodetection while assembling the array
            # will not know what name to give them, so it will name it something
            # like /dev/md126, /dev/md127 rather than /dev/md0, /dev/md1.

            # If the user didn't modify the default (all commented) mdadm.conf file,
            # then they will obviously get wrong raid array numbers being assigned
            # by the kernel. The user needs to run a "mdadm --examine --scan > /etc/mdadm.conf"
            # to fix this, and re-run the initramfs creator.
            mdadm_conf = "/etc/mdadm.conf"
            Tools.CopyConfigOrWarn(mdadm_conf)

        # Enable LVM in the init if LVM is being used
        if Lvm.IsEnabled():
            Tools.ActivateTriggerInInit(var.useLvmLine)

            lvm_conf = "/etc/lvm/lvm.conf"
            Tools.CopyConfigOrWarn(lvm_conf)

        # Enable ZFS in the init if ZFS is being used
        if Zfs.IsEnabled():
            Tools.ActivateTriggerInInit(var.useZfsLine)

        # Enable ADDON in the init and add our modules to the initramfs
        # if addon is being used
        if Addon.IsEnabled():
            Tools.ActivateTriggerInInit(var.useAddonLine)
            call(["sed", "-i", "-e", var.addonModulesLine + "s/\"\"/\"" + " ".join(Addon.GetFiles()) + "\"/", var.temp + "/init"])

        cls.CopyLibGccLibrary()

    # Copy the 'libgcc' library so that when libpthreads loads it during runtime, it works.
    # https://github.com/zfsonlinux/zfs/issues/4749
    @classmethod
    def CopyLibGccLibrary(cls):
        cmd = "gcc-config -L | cut -d ':' -f 1"
        res = Tools.Run(cmd)

        if len(res) < 1:
            Tools.Fail("Unable to retrieve gcc library path!")

        libgcc_filename = "libgcc_s.so"
        libgcc_filename_main = libgcc_filename + ".1"
        libgcc_path = res[0] + "/" + libgcc_filename_main

        Tools.SafeCopy(libgcc_path, var.llib64)
        os.chdir(var.llib64)
        os.symlink(libgcc_filename_main, libgcc_filename)

    # Create the initramfs
    @classmethod
    def CreateInitramfs(cls):
        Tools.Info("Creating the initramfs ...")

        # The find command must use the `find .` and not `find ${T}`
        # because if not, then the initramfs layout will be prefixed with
        # the ${T} path.
        os.chdir(var.temp)

        call(["find . -print0 | cpio -o --null --format=newc | gzip -9 > " + var.home + "/" + var.initrd], shell=True)

        if not os.path.isfile(var.home + "/" + var.initrd):
            Tools.Fail("Error creating the initramfs. Exiting.")

    # Checks to see if the binaries exist, if not then emerge
    @classmethod
    def VerifyBinaries(cls):
        Tools.Info("Checking required files ...")

        # Check required base files
        cls.VerifyBinariesExist(Base.GetFiles())

        # Check required luks files
        if Luks.IsEnabled():
            Tools.Flag("Using LUKS")
            cls.VerifyBinariesExist(Luks.GetFiles())

        # Check required raid files
        if Raid.IsEnabled():
            Tools.Flag("Using RAID")
            cls.VerifyBinariesExist(Raid.GetFiles())

        # Check required lvm files
        if Lvm.IsEnabled():
            Tools.Flag("Using LVM")
            cls.VerifyBinariesExist(Lvm.GetFiles())

        # Check required zfs files
        if Zfs.IsEnabled():
            Tools.Flag("Using ZFS")
            cls.VerifyBinariesExist(Zfs.GetFiles())

    # Checks to see that all the binaries in the array exist and errors if they don't
    @classmethod
    def VerifyBinariesExist(cls, vFiles):
        for file in vFiles:
            if not os.path.exists(file):
                Tools.BinaryDoesntExist(file)

    # Copies the required files into the initramfs
    @classmethod
    def CopyBinaries(cls):
        Tools.Info("Copying binaries ...")

        cls.FilterAndInstall(Base.GetFiles())

        if Luks.IsEnabled():
            cls.FilterAndInstall(Luks.GetFiles())

        if Raid.IsEnabled():
            cls.FilterAndInstall(Raid.GetFiles())

        if Lvm.IsEnabled():
            cls.FilterAndInstall(Lvm.GetFiles())

        if Zfs.IsEnabled():
            cls.FilterAndInstall(Zfs.GetFiles())
            cls.FilterAndInstall(Zfs.GetOptionalFiles(), dontFail=True)

    # Copies the man pages (driver)
    @classmethod
    def CopyManPages(cls):
        if Zfs.IsEnabled() and Zfs.IsManEnabled():
            Tools.Info("Copying man pages ...")
            cls.CopyMan(Zfs.GetManPages())

    # Depending the ZFS version that the user is running,
    # some manual pages that the initramfs wants to copy might not
    # have yet been written. Therefore, attempt to copy the man pages,
    # but if we are unable to copy, then just continue.
    @classmethod
    def CopyMan(cls, files):
        for f in files:
            Tools.Copy(f, dontFail=True)

    # Filters and installs each file in the array into the initramfs
    # Optional Args:
    #   dontFail - Same description as the one in Tools.Copy
    @classmethod
    def FilterAndInstall(cls, vFiles, **optionalArgs):
        for file in vFiles:
            # If the application is a binary, add it to our binary set. If the application is not
            # a binary, then we will get a CalledProcessError because the output will be null.
            try:
                check_output('file -L ' + file.strip() + ' | grep "linked"', shell=True, universal_newlines=True).strip()
                cls._binset.add(file)
            except CalledProcessError:
                pass

            # Copy the file into the initramfs
            Tools.Copy(file, dontFail=optionalArgs.get("dontFail", False))

    # Copy modules and their dependencies
    @classmethod
    def CopyModules(cls):
        moddeps = set()

        # Build the list of module dependencies
        if Addon.IsEnabled():
            Tools.Info("Copying modules ...")

            # Checks to see if all the modules in the list exist
            for file in Addon.GetFiles():
                try:
                    cmd = 'find ' + var.modules + ' -iname "' + file + '.ko" | grep ' + file + '.ko'
                    result = check_output(cmd, universal_newlines=True, shell=True).strip()
                    cls._modset.add(result)
                except CalledProcessError:
                    Tools.ModuleDoesntExist(file)

        # If a kernel has been set, try to update the module dependencies
        # database before searching it
        if var.kernel:
            try:
                result = call(["depmod", var.kernel])

                if result:
                    Tools.Fail("Error updating module dependency database!")
            except FileNotFoundError:
                    # This should never occur because the application checks
                    # that root is the user that is running the application.
                    # Non-administraative users normally don't have access
                    # to the 'depmod' command.
                    Tools.Fail("The 'depmod' command wasn't found.")

        # Get the dependencies for all the modules in our set
        for file in cls._modset:
            # Get only the name of the module
            match = re.search('(?<=/)[a-zA-Z0-9_-]+.ko', file)

            if match:
                sFile = match.group().split(".")[0]

                cmd = "modprobe -S " + var.kernel + " --show-depends " + sFile + " | awk -F ' ' '{print $2}'"
                results = check_output(cmd, shell=True, universal_newlines=True).strip()

                for i in results.split("\n"):
                    moddeps.add(i.strip())

        # Copy the modules/dependencies
        if moddeps:
            for module in moddeps:
                Tools.Copy(module)

            # Update module dependency database inside the initramfs
            cls.GenerateModprobeInfo()

    # Gets the library dependencies for all our binaries and copies them into our initramfs.
    @classmethod
    def CopyDependencies(cls):
        Tools.Info("Copying library dependencies ...")

        bindeps = set()

        # Get the interpreter name that is on this system
        result = check_output("ls " + var.lib64 + "/ld-linux-x86-64.so*", shell=True, universal_newlines=True).strip()

        # Add intepreter to deps since everything will depend on it
        bindeps.add(result)

        # Get the dependencies for the binaries we've collected and add them to
        # our bindeps set. These will all be copied into the initramfs later.
        for binary in cls._binset:
            cmd = "ldd " + binary + " | awk -F '=>' '{print $2}' | awk -F ' ' '{print $1}' | sed '/^ *$/d'"
            results = check_output(cmd, shell=True, universal_newlines=True).strip()

            if results:
                for library in results.split("\n"):
                    bindeps.add(library)

        # Copy all the dependencies of the binary files into the initramfs
        for library in bindeps:
            Tools.Copy(library)
