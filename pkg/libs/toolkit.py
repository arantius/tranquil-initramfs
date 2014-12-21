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
import sys

from subprocess import call
from subprocess import check_output

import pkg.libs.variables as var

class Toolkit:
    # Checks parameters and running user
    @classmethod
    def welcome(cls, core):
        user = check_output(["whoami"], universal_newlines=True).strip()

        if user != "root":
            cls.die("This program must be ran as root")

        arguments = sys.argv[1:]

        # Let the user directly create an initramfs if no modules are needed
        if len(arguments) == 1:
            if arguments[0] != "1" and arguments[0] != "2":
                if not core.addon.get_files():
                    var.choice = arguments[0]
            else:
                cls.die("You must pass a kernel parameter")

        # If there are two parameters then we will use them, else just ignore them
        elif len(arguments) == 2:
            var.choice = arguments[0]
            var.kernel = arguments[1]

    # Prints the header of the application
    @classmethod
    def print_header(cls):
        cls.eprint(cls.colorize("yellow", "----------------------------------"))
        cls.eprint(cls.colorize("yellow", var.name + " - v" + var.version))
        cls.eprint(cls.colorize("yellow", var.contact))
        cls.eprint(cls.colorize("yellow", "Distributed under the " + var.license))
        cls.eprint(cls.colorize("yellow", "----------------------------------") + "\n")

    # Prints the available options
    @classmethod
    def print_options(cls):
        cls.eline()
        cls.eopt("1. ZFS")
        cls.eopt("2. Encrypted ZFS")
        cls.eopt("3. Normal")
        cls.eopt("4. Encrypted Normal")
        cls.eopt("5. Exit Program")
        cls.eline()

    # Finds the path to a program on the system
    @classmethod
    def find_prog(cls, prog):
        cmd = 'whereis ' + prog + ' | cut -d " " -f 2'
        results = check_output(cmd, shell=True, universal_newlines=True).strip()

        if results:
            return results
        else:
            cls.die("The " + prog + " program could not be found!")

    # Returns the path to systemd-udevd
    @classmethod
    def find_udevd(cls):
            udevd_paths = (["/usr/lib/systemd/systemd-udevd","/lib/systemd/systemd-udevd"])

            for path in udevd_paths:
                if os.path.exists(path):
                    return path

            cls.die("udev not found on system!")

    # Check to see if the temporary directory exists, if it does,
    # delete it for a fresh start
    @classmethod
    def clean(cls):
        # Go back to the original working directory so that we are
        # completely sure that there will be no inteference cleaning up.
        os.chdir(var.home)

        # Removes the temporary link created at the start of the app
        if os.path.exists(var.tlink):
            os.remove(var.tlink)

            if os.path.exists(var.tlink):
                cls.ewarn("Failed to delete the temporary link at: " + tlink + ". Exiting.")
                quit(1)

        # Removes the temporary directory
        if os.path.exists(var.temp):
            shutil.rmtree(var.temp)

            if os.path.exists(var.temp):
                cls.ewarn("Failed to delete the " + var.temp + " directory. Exiting.")
                quit(1)

    # Clean up and exit after a successful build
    @classmethod
    def clean_exit(cls, initrd):
        cls.clean()
        cls.einfo("Please copy \"" + initrd + "\" to your " + "/boot directory")
        quit()

    # Intelligently copies the file into the initramfs
    @classmethod
    def ecopy(cls, afile):
        # NOTE: shutil.copy will dereference all symlinks before copying.

        # Check to see if a file with this name exists before copying,
        # if it exists, delete it, then copy. If a directory, create the directory
        # before copying.
        path = var.temp + "/" + afile

        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
                shutil.copy(afile, path)
        else:
            if os.path.isfile(afile):
                # Make sure that the directory that this file wants to be in
                # exists, if not then create it.
                if os.path.isdir(os.path.dirname(path)):
                    shutil.copy(afile, path)
                else:
                    os.makedirs(os.path.dirname(path))
                    shutil.copy(afile, path)
            elif os.path.isdir(afile):
                os.makedirs(path)

        # Finally lets make sure that the file was copied to its destination
        if not os.path.isfile(path):
            cls.die("Unable to copy " + afile + " to " + path + "!")

    ####### Message Functions #######

    # Returns the string with a color to be used in bash
    @staticmethod
    def colorize(color, message):
        if color == "red":
            colored_message = "\e[1;31m" + message + "\e[0;m"
        elif color == "yellow":
            colored_message = "\e[1;33m" + message + "\e[0;m"
        elif color == "green":
            colored_message = "\e[1;32m" + message + "\e[0;m"
        elif color == "cyan":
            colored_message = "\e[1;36m" + message + "\e[0;m"
        elif color == "purple":
            colored_message = "\e[1;34m" + message + "\e[0;m"
        elif color == "none":
            colored_message = message

        return colored_message

    # Prints a message through the shell
    @classmethod
    def eprint(cls, message):
        call(["echo", "-e", message])

    # Used for displaying information
    @classmethod
    def einfo(cls, message):
        call(["echo", "-e", cls.colorize("green", "[*] ") + message])

    # Used for input (questions)
    @classmethod
    def eqst(cls, question):
        return input(question)

    # Used for warnings
    @classmethod
    def ewarn(cls, message):
        call(["echo", "-e", cls.colorize("yellow", "[!] ") + message])

    # Used for flags (aka using zfs, luks, etc)
    @classmethod
    def eflag(cls, flag):
        call(["echo", "-e", cls.colorize("purple", "[+] ") + flag])

    # Used for options
    @classmethod
    def eopt(cls, opt):
        call(["echo", "-e", cls.colorize("cyan", "[>] ") + opt])

    # Used for errors
    @classmethod
    def die(cls, message):
        cls.eprint(cls.colorize("red", "[#] ") + message)
        cls.eline()
        cls.clean()
        quit(1)

    # Prints empty line
    @classmethod
    def eline(cls):
        print("")

    # Error Function: Binary doesn't exist
    @classmethod
    def err_bin_dexi(cls, message):
        cls.die("Binary: " + message + " doesn't exist. Exiting.")

    # Error Function: Module doesn't exist
    @classmethod
    def err_mod_dexi(cls, message):
        cls.die("Module: " + message + " doesn't exist. Exiting.")
