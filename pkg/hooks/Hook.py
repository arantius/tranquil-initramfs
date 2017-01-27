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
