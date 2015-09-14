#!/usr/bin/env python3

# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from subprocess import call

import pkg.libs.Variables as var

from pkg.libs.Core import Core
from pkg.libs.Tools import Tools
from pkg.hooks.Addon import Addon
from pkg.hooks.Lvm import Lvm

class Main:
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
        Core.CopyBinaries()
        Core.CopyManPages()
        Core.CopyModules()
        Core.CopyFirmware()
        Core.CreateLinks()
        Core.CopyDependencies()
        Core.LastSteps()
        Core.CreateInitramfs()
        Tools.CleanAndExit(var.initrd)

if __name__ == '__main__':
    Main.start()
