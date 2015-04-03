# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the Simplified BSD License which can be found in the LICENSE file.

import os
import shutil
import sys

import pkg.libs.Variables as var

from subprocess import call
from subprocess import check_output

class Tools(object):
    # Checks parameters and running user
    @classmethod
    def ProcessArguments(cls, Addon):
        user = check_output(["whoami"], universal_newlines=True).strip()

        if user != "root":
            cls.Fail("This program must be ran as root")

        arguments = sys.argv[1:]

        # Let the user directly create an initramfs if no modules are needed
        if len(arguments) == 1:
            if arguments[0] != "1" and arguments[0] != "2":
                if not Addon.GetFiles():
                    var.choice = arguments[0]
            else:
                cls.Fail("You must pass a kernel parameter")

        # If there are two parameters then we will use them, else just ignore them
        elif len(arguments) == 2:
            var.choice = arguments[0]
            var.kernel = arguments[1]

    # Prints the header of the application
    @classmethod
    def PrintHeader(cls):
        cls.Print(cls.Colorize("yellow", "----------------------------------"))
        cls.Print(cls.Colorize("yellow", var.name + " - v" + var.version))
        cls.Print(cls.Colorize("yellow", var.contact))
        cls.Print(cls.Colorize("yellow", "Licensed under the " + var.license))
        cls.Print(cls.Colorize("yellow", "----------------------------------") + "\n")

    # Prints the available options
    @classmethod
    def PrintOptions(cls):
        cls.NewLine()
        cls.Option("1. ZFS")
        cls.Option("2. Encrypted ZFS")
        cls.Option("3. Normal")
        cls.Option("4. Encrypted Normal")
        cls.Option("5. Exit Program")
        cls.NewLine()

    # Finds the path to a program on the system
    @classmethod
    def GetProgramPath(cls, vProg):
        cmd = 'whereis ' + vProg + ' | cut -d " " -f 2'
        results = check_output(cmd, shell=True, universal_newlines=True).strip()

        if results:
            return results
        else:
            cls.Fail("The " + vProg + " program could not be found!")

    # Returns the path to udev
    @classmethod
    def GetUdevPath(cls):
            udev_paths = [
                "/usr/lib/systemd/systemd-udevd",
                "/lib/systemd/systemd-udevd",
                "/sbin/udevd",
            ]

            for path in udev_paths:
                if os.path.exists(path) and os.path.isfile(path):
                    return path

            cls.Fail("udev was not found on the system!")

    # Check to see if the temporary directory exists, if it does,
    # delete it for a fresh start
    @classmethod
    def Clean(cls):
        # Go back to the original working directory so that we are
        # completely sure that there will be no inteference cleaning up.
        os.chdir(var.home)

        # Removes the temporary link created at the start of the app
        if os.path.exists(var.tlink):
            os.remove(var.tlink)

            if os.path.exists(var.tlink):
                cls.Warn("Failed to delete the temporary link at: " + tlink + ". Exiting.")
                quit(1)

        # Removes the temporary directory
        if os.path.exists(var.temp):
            shutil.rmtree(var.temp)

            if os.path.exists(var.temp):
                cls.Warn("Failed to delete the " + var.temp + " directory. Exiting.")
                quit(1)

    # Clean up and exit after a successful build
    @classmethod
    def CleanAndExit(cls, vInitrd):
        cls.Clean()
        cls.Info("Please copy \"" + vInitrd + "\" to your " + "/boot directory")
        quit()

    # Intelligently copies the file into the initramfs
    @classmethod
    def Copy(cls, vFile, **optionalArgs):
        # NOTE: shutil.copy will dereference all symlinks before copying.

        # If a prefix was passed into the function as an optional argument
        # it will be used below.
        directoryPrefix = optionalArgs.get("directoryPrefix", None)

        # Check to see if a file with this name exists before copying,
        # if it exists, delete it, then copy. If a directory, create the directory
        # before copying.
        if directoryPrefix:
            path =  var.temp + "/" + directoryPrefix + "/" + vFile
            targetFile = directoryPrefix + "/" +  vFile
        else:
            path = var.temp + "/" + vFile
            targetFile = vFile

        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
                shutil.copy(targetFile, path)
        else:
            if os.path.isfile(targetFile):
                # Make sure that the directory that this file wants to be in
                # exists, if not then create it.
                if os.path.isdir(os.path.dirname(path)):
                    shutil.copy(targetFile, path)
                else:
                    os.makedirs(os.path.dirname(path))
                    shutil.copy(targetFile, path)
            elif os.path.isdir(targetFile):
                os.makedirs(path)

        # Finally lets make sure that the file was copied to its destination
        if not os.path.isfile(path):
            cls.Fail("Unable to copy " + targetFile + " to " + path + "!")

    ####### Message Functions #######

    # Returns the string with a color to be used in bash
    @classmethod
    def Colorize(cls, vColor, vMessage):
        if vColor == "red":
            colored_message = "\e[1;31m" + vMessage + "\e[0;m"
        elif vColor == "yellow":
            colored_message = "\e[1;33m" + vMessage + "\e[0;m"
        elif vColor == "green":
            colored_message = "\e[1;32m" + vMessage + "\e[0;m"
        elif vColor == "cyan":
            colored_message = "\e[1;36m" + vMessage + "\e[0;m"
        elif vColor == "purple":
            colored_message = "\e[1;34m" + vMessage + "\e[0;m"
        elif vColor == "none":
            colored_message = vMessage

        return colored_message

    # Prints a message through the shell
    @classmethod
    def Print(cls, vMessage):
        call(["echo", "-e", vMessage])

    # Used for displaying information
    @classmethod
    def Info(cls, vMessage):
        call(["echo", "-e", cls.Colorize("green", "[*] ") + vMessage])

    # Used for input (questions)
    @classmethod
    def Question(cls, vQuestion):
        return input(vQuestion)

    # Used for warnings
    @classmethod
    def Warn(cls, vMessage):
        call(["echo", "-e", cls.Colorize("yellow", "[!] ") + vMessage])

    # Used for flags (aka using zfs, luks, etc)
    @classmethod
    def Flag(cls, vFlag):
        call(["echo", "-e", cls.Colorize("purple", "[+] ") + vFlag])

    # Used for options
    @classmethod
    def Option(cls, vOption):
        call(["echo", "-e", cls.Colorize("cyan", "[>] ") + vOption])

    # Used for errors
    @classmethod
    def Fail(cls, vMessage):
        cls.Print(cls.Colorize("red", "[#] ") + vMessage)
        cls.NewLine()
        cls.Clean()
        quit(1)

    # Prints empty line
    @classmethod
    def NewLine(cls):
        print("")

    # Error Function: Binary doesn't exist
    @classmethod
    def BinaryDoesntExist(cls, vMessage):
        cls.Fail("Binary: " + vMessage + " doesn't exist. Exiting.")

    # Error Function: Module doesn't exist
    @classmethod
    def ModuleDoesntExist(cls, vMessage):
        cls.Fail("Module: " + vMessage + " doesn't exist. Exiting.")
