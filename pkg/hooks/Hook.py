# Copyright 2012-2017 Jonathan Vasquez <jon@xyinn.org>
# 
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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
