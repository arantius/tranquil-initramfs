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

from pkg.libs.toolkit import Toolkit as tools

class Hook:
    def __init__(self):
        self.use = 0
        self.files = []

    # Enables the use value
    def enable_use(self):
        self.use = 1

    # Disables the use value
    def disable_use(self):
        self.use = 0

    # Gets the use value
    def get_use(self):
        return self.use

    # Adds a file to the list
    def add_to_files(self, afile):
        self.files.append(afile)

    # Deletes a file from the list
    def remove_from_files(self, afile):
        try:
            self.files.remove(afile)
        except ValueError:
            tools.die("The file \"" + afile + "\" was not found on the list!")

    # Prints the files in the list
    def print_files(self):
        for i in self.files:
            print("File: " + i)

    # Returns the list
    def get_files(self):
        return self.files
