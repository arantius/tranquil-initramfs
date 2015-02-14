#!/usr/bin/env python3

# Copyright 2012-2015 Jonathan Vasquez <jvasquez1011@gmail.com>
# Licensed under the Simplified BSD License which can be found in the LICENSE file.

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
