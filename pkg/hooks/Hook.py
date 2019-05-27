# Copyright (C) 2012-2019 Jonathan Vasquez <jon@xyinn.org>
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
