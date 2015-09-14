# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from pkg.libs.Tools import Tools

class Hook:
    _use = 0
    _use_man = 0
    _files = []
    _optional_files = []
    _man = []

    # Enables the use value
    @classmethod
    def Enable(cls):
        cls._use = 1

    # Disables the use value
    @classmethod
    def Disable(cls):
        cls._use = 0

    # Enables copying the man pages
    @classmethod
    def EnableMan(cls):
        cls._use_man = 1

    # Enables copying the man pages
    @classmethod
    def DisableMan(cls):
        cls._use_man = 0

    # Gets the use value
    @classmethod
    def IsEnabled(cls):
        return cls._use

    # Gets the copy man pages value
    @classmethod
    def IsManEnabled(cls):
        return cls._use_man

    # Adds a file to the list
    @classmethod
    def AddFile(cls, vFile):
        cls._files.append(vFile)

    # Deletes a file from the list
    @classmethod
    def RemoveFile(cls, vFile):
        try:
            cls._files.remove(vFile)
        except ValueError:
            Tools.Fail("The file \"" + vFile + "\" was not found on the list!")

    # Prints the files in the list
    @classmethod
    def PrintFiles(cls):
        for file in cls.GetFiles():
            print("File: " + file)

    # Returns the list of required files
    @classmethod
    def GetFiles(cls):
        return cls._files

    # Returns the list of optional files
    @classmethod
    def GetOptionalFiles(cls):
        return cls._optional_files

    # Returns the list of manuals
    @classmethod
    def GetManPages(cls):
        return cls._man
