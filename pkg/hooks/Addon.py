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

from pkg.hooks.Hook import Hook

class Addon(Hook):
    # A list of kernel modules to include in the initramfs
    # Format: "module1", "module2", "module3", ...
    _files = [
        # Uncomment the module below if you have encryption support built as a module, rather than built into the kernel:
        #"dm-crypt",

        # Add your modules below
        #"i915",
        #"nouveau",
    ]
