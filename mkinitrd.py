#!/usr/bin/env python3

# Copyright (C) 2012-2018 Jonathan Vasquez <jon@xyinn.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see<https://www.gnu.org/licenses/>.

from subprocess import call

import pkg.libs.Variables as var

from pkg.libs.Core import Core
from pkg.libs.Tools import Tools
from pkg.hooks.Addon import Addon

class Main:
    # Let the games begin ...
    @classmethod
    def start(cls):
        Tools.ProcessArguments(Addon)
        call(["clear"])
        Tools.PrintHeader()
        Core.PrintMenuAndGetDesiredFeatures()

        if var.kernel or Addon.GetFiles():
            Core.GetDesiredKernel()

        Core.VerifySupportedArchitecture()
        Tools.Clean()
        Core.VerifyPreliminaryBinaries()
        Core.CreateBaselayout()
        Core.VerifyBinaries()
        Core.CopyBinaries()
        Core.CopyManPages()
        Core.CopyModules()
        Core.CopyFirmware()

        # Dependencies must be copied before we create links since the commands inside of
        # the create links (i.e chroot) function require that the libraries are already
        # in our chroot environment.
        Core.CopyDependencies()
        Core.CreateLinks()

        Core.LastSteps()
        Core.CreateInitramfs()
        Tools.CleanAndExit(var.initrd)

if __name__ == '__main__':
    Main.start()
