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

import configparser
import getpass
import glob
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
from pkg.hooks.Zfs import Zfs
from pkg.hooks.Modules import Modules
from pkg.hooks.Firmware import Firmware

# Contains the core of the application
class Core:
    # List of binaries (That will be 'ldd'ed later)
    _binset = set()

    # List of modules that will be compressed
    _modset = set()

    # Enable the 'base' hook since all initramfs will have this
    Base.Enable()

    # Modules will now always be enabled since all initramfs can have
    # the ability to have 0 or more modules.
    Modules.Enable()

    @classmethod
    def LoadConfig(cls):
      """Load `config.ini` settings into each hook."""
      config = configparser.ConfigParser(allow_no_value=True)
      config.read([var.config_default_file, var.config_file])

      Base.LoadConfig(config)
      Firmware.LoadConfig(config)
      Luks.LoadConfig(config)
      Modules.LoadConfig(config)
      Zfs.LoadConfig(config)

      var.features = []
      if config['Luks'].getboolean('include', True):
        var.features.append('luks')
        Luks.Enable()
      if config['Zfs'].getboolean('include', True):
        var.features.append('zfs')
        Zfs.Enable()
        Modules.AddFile("zfs")

    # Returns the name equivalent list of a numbered list of features
    @classmethod
    def ConvertNumberedFeaturesToNamedList(cls, numbered_feature_list):
        named_features = []

        try:
            for feature in numbered_feature_list.split(","):
                feature_as_string = Tools._features[int(feature)].lower()
                named_features.append(feature_as_string)
        except KeyError:
            named_features.clear()
            named_features.append("exit")

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
            current_kernel = check_output(
                ["uname", "-r"], universal_newlines=True
            ).strip()

            message = (
                "Do you want to use the current kernel: " + current_kernel + " [Y/n]: "
            )
            choice = Tools.Question(message)
            Tools.NewLine()

            if choice == "y" or choice == "Y" or not choice:
                var.kernel = current_kernel
            elif choice == "n" or choice == "N":
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
            if not os.path.isfile(Tools.GetProgramPath(binary)):
                Tools.BinaryDoesntExist(binary)

    # Generates the modprobe information
    @classmethod
    def GenerateModprobeInfo(cls):
        Tools.Info("Generating modprobe information ...")

        # Copy modules.order and modules.builtin just so depmod doesn't spit out warnings. -_-
        Tools.Copy(var.modules + "/modules.order")
        Tools.Copy(var.modules + "/modules.builtin")

        cmd_ = ["depmod", "-b", var.temp, var.kernel]
        cls.SudoWrapCommand(cmd_)
        result = call(cmd_)

        if result != 0:
            Tools.Fail(
                "Depmod was unable to refresh the dependency information for your initramfs!"
            )

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
                            Tools.Warn(
                                "An error occured while copying the following firmware: "
                                + fw
                            )
                    else:
                        Tools.Warn("No firmware files were found in the firmware list!")
            else:
                Tools.Fail("The /lib/firmware/ directory does not exist")

    # Create the required symlinks
    @classmethod
    def CreateLinks(cls):
        Tools.Info("Creating symlinks ...")

        # Create busybox links
        for applet in Tools.Run(var.temp + '/bin/busybox --list'):
          if applet == 'busybox': continue
          if os.path.exists(var.lbin + '/' + applet): continue
          os.symlink('busybox', var.lbin + '/' + applet)

        # Create 'sh' symlink to 'bash'
        os.remove(var.lbin + '/sh')
        os.symlink('bash', var.lbin + '/sh')

        # Replace busybox symlinks and with kmod
        dest = '/bin/'
        if os.path.isfile(var.lsbin + "/kmod"):
            dest = '/sbin/'
        for link in Base.GetKmodLinks():
            os.remove(var.lbin + '/' + link)
            os.symlink("kmod", var.temp + dest + link)

    # Creates symlinks from library files found in each /usr/lib## dir to the /lib[32/64] directories
    @classmethod
    def CreateLibraryLinks(cls):
        cwd = os.getcwd()
        os.chdir(var.temp)
        for (src, dst) in (
                ('/usr/lib', '/lib64'),
                ('/usr/lib32', '/lib32'),
                ('/usr/lib64', '/lib64'),
                ('/lib', '/lib'),
                ):
            if os.path.isdir(var.temp + src) and os.path.isdir(var.temp + dst):
                cls.FindAndCreateLinks(src, dst)
        os.chdir(cwd)

    @classmethod
    def FindAndCreateLinks(cls, sourceDirectory, targetDirectory):
        for p in ('/**/*.so.*', '/**/*.so'):
          for f in glob.glob('.' + sourceDirectory + p, recursive=True):
            dst = var.temp + targetDirectory + '/' + os.path.basename(f)
            os.symlink(f[1:], dst)

    # Copies udev and files that udev uses, like /etc/udev/*, /lib/udev/*, etc
    @classmethod
    def CopyUdevAndSupportFiles(cls):
        # Copy all of the udev files
        udev_conf_dir = "/etc/udev/"
        temp_udev_conf_dir = var.temp + udev_conf_dir

        if os.path.isdir(udev_conf_dir):
            shutil.copytree(udev_conf_dir, temp_udev_conf_dir)

        udev_lib_dir = "/lib/udev/"
        temp_udev_lib_dir = var.temp + udev_lib_dir

        if os.path.isdir(udev_lib_dir):
            shutil.copytree(udev_lib_dir, temp_udev_lib_dir)

        # Rename udevd and place in /sbin
        udev_path = Tools.GetUdevPath()
        systemd_dir = os.path.dirname(udev_path)

        sbin_udevd = var.sbin + "/udevd"
        udev_path_temp = var.temp + udev_path

        if os.path.isfile(udev_path_temp) and udev_path != sbin_udevd:
            udev_path_new = var.temp + sbin_udevd
            os.rename(udev_path_temp, udev_path_new)

            temp_systemd_dir = var.temp + systemd_dir

            # If the directory is empty, than remove it.
            # With the recent gentoo systemd root prefix move, it is moving to
            # /lib/systemd. Thus this directory also contains systemd dependencies
            # such as: libsystemd-shared-###.so
            # https://gentoo.org/support/news-items/2017-07-16-systemd-rootprefix.html
            if not os.listdir(temp_systemd_dir):
                os.rmdir(temp_systemd_dir)

    # Dumps the current system's keymap
    @classmethod
    def DumpSystemKeymap(cls):
        pathToKeymap = var.temp + "/etc/keymap"
        result = call("sudo dumpkeys > " + pathToKeymap, shell=True)
        if result != 0 or not os.path.isfile(pathToKeymap):
            Tools.Warn(
                "There was an error dumping the system's current keymap. Ignoring."
            )

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
            Tools.Fail("Failed to give execute privileges to " + var.temp + "/init")

        # Sets initramfs script version number
        cmd = f"echo {var.version} > {var.temp}/version.tranquil"
        call(cmd, shell=True)

        # Copy all of the modprobe configurations
        if os.path.isdir("/etc/modprobe.d/"):
            shutil.copytree("/etc/modprobe.d/", var.temp + "/etc/modprobe.d/")

        cls.CopyUdevAndSupportFiles()
        cls.DumpSystemKeymap()

        # Any last substitutions or additions/modifications should be done here

        if Luks.IsEnabled():
            # Copy over our keyfile if the user activated it
            if Luks.IsKeyfileEnabled():
                Tools.Flag("Embedding our keyfile into the initramfs...")
                Tools.SafeCopy(Luks.GetKeyfilePath(), var.temp + "/etc", "keyfile")

            # Copy over our detached header if the user activated it
            if Luks.IsDetachedHeaderEnabled():
                Tools.Flag("Embedding our detached header into the initramfs...")
                Tools.SafeCopy(
                    Luks.GetDetachedHeaderPath(), var.temp + "/etc", "header"
                )

        # Add any modules needed into the initramfs
        requiredModules = ",".join(Modules.GetFiles())
        cmd = f"echo {requiredModules} > {var.temp}/modules.tranquil"
        call(cmd, shell=True)

        cls.CopyLibGccLibrary()

    # Copy the 'libgcc' library so that when libpthreads loads it during runtime.
    # https://github.com/zfsonlinux/zfs/issues/4749
    @classmethod
    def CopyLibGccLibrary(cls):
        # Find the correct path for libgcc
        libgcc_filename = "libgcc_s.so"
        libgcc_filename_main = libgcc_filename + ".1"

        # check for gcc-config
        cmd = 'whereis gcc-config | cut -d " " -f 2'
        res = Tools.Run(cmd)

        if res:
            # Try gcc-config
            cmd = "gcc-config -L | cut -d ':' -f 1"
            res = Tools.Run(cmd)

            if res:
                # Use path from gcc-config
                libgcc_path = res[0] + "/" + libgcc_filename_main
                Tools.SafeCopy(libgcc_path, var.llib64)
                os.chdir(var.llib64)
                os.symlink(libgcc_filename_main, libgcc_filename)
                return

        # Doing a 'whereis <name of libgcc library>' will not work because it seems
        # that it finds libraries in /lib, /lib64, /usr/lib, /usr/lib64, but not in
        # /usr/lib/gcc/ (x86_64-pc-linux-gnu/5.4.0, etc)

        # When a better approach is found, we can plug it in here directly and return
        # in the event that it succeeds. If it fails, we just continue execution
        # until the end of the function.

        # If we've reached this point, we have failed to copy the gcc library.
        Tools.Fail("Unable to retrieve the gcc library path!")

    # Create the initramfs
    @classmethod
    def CreateInitramfs(cls):
        Tools.Info("Creating the initramfs ...")

        # The find command must use the `find .` and not `find ${T}`
        # because if not, then the initramfs layout will be prefixed with
        # the ${T} path.
        os.chdir(var.temp)

        rc = call(
            [
                (
                "find . -print0 "
                "| sudo cpio -o --null --format=newc "
                "| gzip -9 > "
                )
                + var.home
                + "/"
                + var.initrd
            ],
            shell=True,
        )

        if not os.path.isfile(var.home + "/" + var.initrd):
            Tools.Fail("Error creating the initramfs. Exiting.")

    @staticmethod
    def SudoWrapCommand(cmd_):
        if getpass.getuser() != 'root':
            cmd_.insert(0, 'sudo')

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
                check_output(
                    "file -L " + file.strip() + ' | grep "linked"',
                    shell=True,
                    universal_newlines=True,
                ).strip()
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
        Tools.Info("Copying modules ...")

        # Checks to see if all the modules in the list exist (if any)
        for file in Modules.GetFiles():
            try:
                cmd = (
                    "find "
                    + var.modules
                    + ' -iname "'
                    + file
                    + '.ko" | grep '
                    + file
                    + ".ko"
                )
                result = check_output(cmd, universal_newlines=True, shell=True).strip()
                cls._modset.add(result)
            except CalledProcessError:
                Tools.ModuleDoesntExist(file)

        # If a kernel has been set, try to update the module dependencies
        # database before searching it
        if var.kernel:
            try:
                cmd_ = ["depmod", var.kernel]
                cls.SudoWrapCommand(cmd_)
                result = call(cmd_)

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
            match = re.search("(?<=/)[a-zA-Z0-9_-]+.ko", file)

            if match:
                sFile = match.group().split(".")[0]

                cmd_ = [
                    "modprobe", "-S", var.kernel, "--show-depends", sFile]
                cls.SudoWrapCommand(cmd_)
                results = check_output(cmd_, universal_newlines=True)

                for v in results.strip().splitlines():
                    v = v.split()
                    moddeps.add(v[1])

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

        # Musl and non-musl systems are supported.
        possible_libc_paths = [
            var.lib64 + "/ld-linux-x86-64.so*",
            var.lib + "/ld-musl-x86_64.so*",
        ]
        libc_found = False

        for libc in possible_libc_paths:
            try:
                # (Dirty implementation) Use the exit code of grep with no messages being outputed to see if this interpreter exists.
                # We don't know the name yet which is why we are using the wildcard in the variable declaration.
                result = call("grep -Uqs thiswillnevermatch " + libc, shell=True)

                # 0 = match found
                # 1 = file exists but not found
                # 2 = file doesn't exist
                # In situations 0 or 1, we are good, since we just care that the file exists.
                if result != 0 and result != 1:
                    continue

                # Get the interpreter name that is on this system
                result = check_output(
                    "ls " + libc, shell=True, universal_newlines=True
                ).strip()

                # Add intepreter to deps since everything will depend on it
                bindeps.add(result)
                libc_found = True
            except Exception as e:
                pass

        if not libc_found:
            Tools.Fail("No libc interpreters were found!")

        # Get the dependencies for the binaries we've collected and add them to
        # our bindeps set. These will all be copied into the initramfs later.
        for binary in cls._binset:
            cmd = (
                "ldd "
                + binary
                + " | awk -F '=>' '{print $2}' | awk -F ' ' '{print $1}' | sed '/^ *$/d'"
            )
            results = check_output(cmd, shell=True, universal_newlines=True).strip()

            if results:
                for library in results.split("\n"):
                    bindeps.add(library)

        # Copy all the dependencies of the binary files into the initramfs
        for library in bindeps:
            Tools.Copy(library)
