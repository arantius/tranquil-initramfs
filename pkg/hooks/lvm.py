#!/usr/bin/env python

# Copyright (C) 2012-2014 Jonathan Vasquez <fearedbliss@funtoo.org>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
from ..libs.variables import *

# Enable/Disable Hook
use = "0"

# Required Files
files = [

]

# Add the static lvm to the files list if it exists,
# otherwise add the dynamically-linked lvm if it exists
if os.path.exists("/sbin/lvm.static"):
    files.append("/sbin/lvm.static")
elif os.path.exists("/sbin/lvm"):
    files.append("/sbin/lvm")
