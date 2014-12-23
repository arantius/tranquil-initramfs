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
import shutil
import re

from subprocess import call
from subprocess import check_output
from subprocess import CalledProcessError

import pkg.libs.Variables as var

from pkg.libs.Tools import Tools

from pkg.hooks.Base import Base
from pkg.hooks.Zfs import Zfs
from pkg.hooks.Luks import Luks
from pkg.hooks.Addon import Addon
from pkg.hooks.Firmware import Firmware
from pkg.hooks.Udev import Udev

# Contains the core of the application
class Core(object):
     # List of binaries (That will be 'ldd'ed later)
    _binset = set()

    # List of modules that will be compressed
    _modset = set()

    # Enable the 'base' hook since all initramfs will have this
    Base.Enable()

    @classmethod
    # Prints the menu and accepts user choice
    def PrintMenu(cls):
        # If the user didn't pass an option through the command line,
        # then ask them which initramfs they would like to generate.
        if not var.choice:
            print("Which initramfs would you like to generate:")
            Tools.PrintOptions()
            var.choice = Tools.Question("Current choice [1]: ")
            Tools.NewLine()

        # Enable the addons if the addon has files (modules) listed
        if Addon.GetFiles():
            Addon.Enable()

        # ZFS
        if var.choice == "1" or not var.choice:
            Zfs.Enable()
            Addon.Enable()
            Addon.AddFile("zfs")
        # Encrypted ZFS
        elif var.choice == "2":
            Luks.Enable()
            Zfs.Enable()
            Addon.Enable()
            Addon.AddFile("zfs")
        # Normal
        elif var.choice == "3":
            pass
        # Encrypted Normal
        elif var.choice == "4":
            Luks.Enable()
        # Exit
        elif var.choice == "5":
            Tools.Warn("Exiting.")
            quit(1)
        # Invalid Option
        else:
            Tools.Warn("Invalid Option. Exiting.")
            quit(1)

    ## Creates the base directory structure
    #def create_baselayout(self):
        #for b in var.baselayout:
            #call(["mkdir", "-p", b])

        ## Create a symlink to this temporary directory at the home dir.
        ## This will help us debug if anything (since the dirs are randomly
        ## generated...)
        #os.symlink(var.temp, var.tlink)

    # Ask the user if they want to use their current kernel, or another one
    @classmethod
    def GetDesiredKernel(cls):
        if not var.kernel:
            current_kernel = check_output(["uname", "-r"], universal_newlines=True).strip()

            message = "Do you want to use the current kernel: " + current_kernel + " [Y/n]: "
            var.choice = Tools.Question(message)
            Tools.NewLine()

            if var.choice == 'y' or var.choice == 'Y' or not var.choice:
                var.kernel = current_kernel
            elif var.choice == 'n' or var.choice == 'N':
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

    ## Make sure that the arch is x86_64
    #def get_arch(self):
        #if var.arch != "x86_64":
            #Tools.Fail("Your architecture isn't supported. Exiting.")

    ## Checks to see if the preliminary binaries exist
    #def check_prelim_binaries(self):
        #Tools.einfo("Checking preliminary binaries ...")

        ## If the required binaries don't exist, then exit
        #for x in var.prel_bin:
            #if not os.path.isfile(x):
                #Tools.err_bin_dexi(x)

    ## Compresses the kernel modules and generates modprobe table
    #def do_modules(self):
        #Tools.einfo("Compressing kernel modules ...")

        #cmd = "find " + var.lmodules + " -name " + "*.ko"
        #results = check_output(cmd, shell=True, universal_newlines=True).strip()

        #for x in results.split("\n"):
            #cmd = "gzip -9 " + x
            #cr = call(cmd, shell=True)

            #if cr != 0:
                #Tools.Fail("Unable to compress " + x + " !")

    ## Generates the modprobe information
    #def gen_modinfo(self):
        #Tools.einfo("Generating modprobe information ...")

        ## Copy modules.order and modules.builtin just so depmod doesn't spit out warnings. -_-
        #Tools.ecopy(var.modules + "/modules.order")
        #Tools.ecopy(var.modules + "/modules.builtin")

        #result = call(["depmod", "-b", var.temp, var.kernel])

        #if result != 0:
            #Tools.Fail("Depmod was unable to refresh the dependency information for your initramfs!")

    ## Copies the firmware files if necessary
    #def copy_firmware(self):
        #if self.firmware.get_use():
            #Tools.einfo("Copying firmware...")

            #if os.path.isdir("/lib/firmware/"):
                #if self.firmware.is_copy_all():
                    #shutil.copytree("/lib/firmware/", var.temp + "/lib/firmware/")
                #else:
                    ## copy the firmware in the files list
                    #if self.firmware.get_files():
                        #try:
                            #for fw in self.firmware.get_files():
                                #Tools.ecopy(fw)
                        #except FileNotFoundError:
                            #Tools.ewarn("An error occured while copying the following firmware: " + fw)
                    #else:
                        #Tools.ewarn("No firmware files were found in the firmware list!")
            #else:
                #Tools.Fail("The /lib/firmware/ directory does not exist")

    ## Create the required symlinks
    #def create_links(self):
        #Tools.einfo("Creating symlinks ...")

        ## Needs to be from this directory so that the links are relative
        #os.chdir(var.lbin)

        ## Create busybox links
        #cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "cd /bin && /bin/busybox --install -s ."'

        #cr = call(cmd, shell=True)

        #if cr != 0:
            #Tools.Fail("Unable to create busybox links via chroot!")

        ## Create 'sh' symlink to 'bash'
        #os.remove(var.temp + "/bin/sh")
        #os.symlink("bash", "sh")

        ## Switch to the kmod directory, delete the corresponding busybox
        ## symlink and create the symlinks pointing to kmod
        #if os.path.isfile(var.lsbin + "/kmod"):
            #os.chdir(var.lsbin)
        #elif os.path.isfile(var.lbin + "/kmod"):
            #os.chdir(var.lbin)

        #for link in self.base.get_kmod_links():
            #os.remove(var.temp + "/bin/" + link)
            #os.symlink("kmod", link)

    ## This functions does any last minute steps like copying zfs.conf,
    ## giving init execute permissions, setting up symlinks, etc
    #def last_steps(self):
        #Tools.einfo("Performing finishing steps ...")

        ## Create mtab file
        #call(["touch", var.temp + "/etc/mtab"])

        #if not os.path.isfile(var.temp + "/etc/mtab"):
            #Tools.Fail("Error creating the mtab file. Exiting.")

        ## Set library symlinks
        #if os.path.isdir(var.temp + "/usr/lib") and os.path.isdir(var.temp + "/lib64"):
            #pcmd = 'find /usr/lib -iname "*.so.*" -exec ln -s "{}" /lib64 \;'
            #cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "' + pcmd + '"'
            #call(cmd, shell=True)

        #if os.path.isdir(var.temp + "/usr/lib32") and os.path.isdir(var.temp + "/lib32"):
            #pcmd = 'find /usr/lib32 -iname "*.so.*" -exec ln -s "{}" /lib32 \;'
            #cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "' + pcmd + '"'
            #call(cmd, shell=True)

        #if os.path.isdir(var.temp + "/usr/lib64") and os.path.isdir(var.temp + "/lib64"):
            #pcmd = 'find /usr/lib64 -iname "*.so.*" -exec ln -s "{}" /lib64 \;'
            #cmd = 'chroot ' + var.temp + ' /bin/busybox sh -c "' + pcmd + '"'
            #call(cmd, shell=True)

        ## Copy the init script
        #shutil.copy(var.phome + "/files/init", var.temp)

        #if not os.path.isfile(var.temp + "/init"):
            #Tools.Fail("Error creating the init file. Exiting.")

        ## Give execute permissions to the script
        #cr = call(["chmod", "u+x", var.temp + "/init"])

        #if cr != 0:
            #Tools.Fail("Failed to give executive privileges to " + var.temp + "/init")

        ## Fix 'poweroff, reboot' commands
        #call("sed -i \"71a alias reboot='reboot -f' \" " + var.temp + "/etc/bash/bashrc", shell=True)
        #call("sed -i \"71a alias poweroff='poweroff -f' \" " + var.temp + "/etc/bash/bashrc", shell=True)

        ## Sets initramfs script version number
        #call(["sed", "-i", "-e", "22s/0/" + var.version + "/", var.temp + "/init"])

        ## Fix EDITOR/PAGER
        #call(["sed", "-i", "-e", "12s:/bin/nano:/bin/vi:", var.temp + "/etc/profile"])
        #call(["sed", "-i", "-e", "13s:/usr/bin/less:/bin/less:", var.temp + "/etc/profile"])

        ## Copy all of the modprobe configurations
        #if os.path.isdir("/etc/modprobe.d/"):
            #shutil.copytree("/etc/modprobe.d/", var.temp + "/etc/modprobe.d/")

        ## Copy all of the udev files
        #if os.path.isdir("/etc/udev/"):
            #shutil.copytree("/etc/udev/", var.temp + "/etc/udev/")

        #if os.path.isdir("/lib/udev/"):
            #shutil.copytree("/lib/udev/", var.temp + "/lib/udev/")

        ## Rename udevd and place in /sbin
        #systemd_dir = os.path.dirname(Tools.GetUdevPath())

        #if os.path.isfile(var.temp + self.base.udev_path) and Tools.GetUdevPath() != "/sbin/udevd":
            #os.rename(var.temp + self.base.udev_path, var.temp + "/sbin/udevd")
            #os.rmdir(var.temp + systemd_dir)

        ## Any last substitutions or additions/modifications should be done here
        #if self.zfs.get_use():
            ## Enable ZFS in the init if ZFS is being used
            #call(["sed", "-i", "-e", "18s/0/1/", var.temp + "/init"])

            ## Copy zpool.cache into initramfs
            #if os.path.isfile("/etc/zfs/zpool.cache"):
                #Tools.ewarn("Using your zpool.cache file ...")
                #Tools.ecopy("/etc/zfs/zpool.cache")
            #else:
                #Tools.ewarn("No zpool.cache was found. It will not be used ...")

        ## Enable LUKS in the init if LUKS is being used
        #if self.luks.get_use():
            #call(["sed", "-i", "-e", "19s/0/1/", var.temp + "/init"])

        ## Enable ADDON in the init and add our modules to the initramfs
        ## if addon is being used
        #if self.addon.get_use():
            #call(["sed", "-i", "-e", "20s/0/1/", var.temp + "/init"])
            #call(["sed", "-i", "-e", "45s/\"\"/\"" + " ".join(self.addon.get_files()) + "\"/", var.temp + "/init"])

    ## Create the solution
    #def create(self):
        #Tools.einfo("Creating the initramfs ...")

        ## The find command must use the `find .` and not `find ${T}`
        ## because if not, then the initramfs layout will be prefixed with
        ## the ${T} path.
        #os.chdir(var.temp)

        #call(["find . -print0 | cpio -o --null --format=newc | gzip -9 > " +  var.home + "/" + var.initrd], shell=True)

        #if not os.path.isfile(var.home + "/" + var.initrd):
            #Tools.Fail("Error creating the initramfs. Exiting.")

    ## Checks to see if the binaries exist, if not then emerge
    #def check_binaries(self):
        #Tools.einfo("Checking required files ...")

        ## Check required base files
        #for f in self.base.get_files():
            #if not os.path.exists(f):
                #Tools.err_bin_dexi(f)

        ## Check required zfs files
        #if self.zfs.get_use():
            #Tools.eflag("Using ZFS")
            #for f in self.zfs.get_files():
                #if not os.path.exists(f):
                    #Tools.err_bin_dexi(f)

        ## Check required luks files
        #if self.luks.get_use():
            #Tools.eflag("Using LUKS")
            #for f in self.luks.get_files():
                #if not os.path.exists(f):
                    #Tools.err_bin_dexi(f)

    ## Installs the packages
    #def install(self):
        #Tools.einfo("Copying required files ...")

        #for f in self.base.get_files():
            #self.emerge(f)

        #if self.zfs.get_use():
            #for f in self.zfs.get_files():
                #self.emerge(f)

        #if self.luks.get_use():
            #for f in self.luks.get_files():
                #self.emerge(f)

    ## Filters and installs a package into the initramfs
    #def emerge(self, afile):
        ## If the application is a binary, add it to our binary set
        #try:
            #lcmd = check_output('file -L ' + afile.strip() + ' | grep "linked"', shell=True, universal_newlines=True).strip()
            #self.binset.add(afile)
        #except CalledProcessError:
            #pass

        ## Copy the file into the initramfs
        #Tools.ecopy(afile)

    ## Copy modules and their dependencies
    #def copy_modules(self):
        #moddeps = set()

        ## Build the list of module dependencies
        #if self.addon.get_use():
            #Tools.einfo("Copying modules ...")

            ## Checks to see if all the modules in the list exist
            #for x in self.addon.get_files():
                #try:
                    #cmd = 'find ' + var.modules + ' -iname "' + x + '.ko" | grep ' + x + '.ko'
                    #result = check_output(cmd, universal_newlines=True, shell=True).strip()
                    #self.modset.add(result)
                #except CalledProcessError:
                    #Tools.err_mod_dexi(x)

        ## If a kernel has been set, try to update the module dependencies
        ## database before searching it
        #if var.kernel:
            #result = call(["depmod", var.kernel])

            #if result:
                #Tools.Fail("Error updating module dependency database!")

        ## Get the dependencies for all the modules in our set
        #for x in self.modset:
            ## Get only the name of the module
            #match = re.search('(?<=/)\w+.ko', x)

            #if match:
                #sx = match.group().split(".")[0]

                #cmd = "modprobe -S " + var.kernel + " --show-depends " + sx + " | awk -F ' ' '{print $2}'"
                #results = check_output(cmd, shell=True, universal_newlines=True).strip()

                #for i in results.split("\n"):
                    #moddeps.add(i.strip())

        ## Copy the modules/dependencies
        #if moddeps:
            #for x in moddeps:
                #Tools.ecopy(x)

            ## Compress the modules and update module dependency database inside the initramfs
            #self.do_modules()
            #self.gen_modinfo()

    ## Gets the library dependencies for all our binaries and copies them
    ## into our initramfs.
    #def copy_deps(self):
        #Tools.einfo("Copying library dependencies ...")

        #bindeps = set()

        ## Get the interpreter name that is on this system
        #result = check_output("ls " + var.lib64 + "/ld-linux-x86-64.so*", shell=True, universal_newlines=True).strip()

        ## Add intepreter to deps since everything will depend on it
        #bindeps.add(result)

        ## Get the dependencies for the binaries we've collected and add them to
        ## our bindeps set. These will all be copied into the initramfs later.
        #for b in self.binset:
            #cmd = "ldd " + b + " | awk -F '=>' '{print $2}' | awk -F ' ' '{print $1}' | sed '/^ *$/d'"
            #results = check_output(cmd, shell=True, universal_newlines=True).strip()

            #if results:
                #for j in results.split("\n"):
                    #bindeps.add(j)

        ## Copy all the dependencies of the binary files into the initramfs
        #for x in bindeps:
            #Tools.ecopy(x)
