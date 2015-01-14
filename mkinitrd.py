#!/usr/bin/env python3

# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, see <http://www.gnu.org/licenses/>.

from subprocess import call

import pkg.libs.Variables as var

from pkg.libs.Core import Core
from pkg.libs.Tools import Tools
from pkg.hooks.Addon import Addon

class Main(object):
    # Let the games begin ...
    @classmethod
    def start(cls):
        Tools.ProcessArguments(Addon)
        call(["clear"])
        Tools.PrintHeader()
        Core.PrintMenu()

        if var.kernel or Addon.GetFiles():
            Core.GetDesiredKernel()

        Core.VerifySupportedArchitecture()
        Tools.Clean()
        Core.VerifyPreliminaryBinaries()
        Core.CreateBaselayout()
        Core.VerifyBinaries()
        Core.CopyRequiredFiles()
        Core.CopyModules()
        Core.CopyFirmware()
        Core.CreateLinks()
        Core.CopyDependencies()
        Core.LastSteps()
        Core.CreateInitramfs()
        Tools.CleanAndExit(var.initrd)

if __name__ == '__main__':
    Main.start()
