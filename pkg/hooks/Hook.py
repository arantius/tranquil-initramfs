# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the Simplified BSD License which can be found in the LICENSE file.

from pkg.libs.Tools import Tools

class Hook(object):
    _use = 0
    _files = []

    # Enables the use value
    @classmethod
    def Enable(cls):
        cls._use = 1

    # Disables the use value
    @classmethod
    def Disable(cls):
        cls._use = 0

    # Gets the use value
    @classmethod
    def IsEnabled(cls):
        return cls._use

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

    # Returns the list
    @classmethod
    def GetFiles(cls):
        return cls._files
