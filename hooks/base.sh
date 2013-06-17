# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Required Binaries, Modules, and other files
USE_BASE="1"
BASE_BINS="
	${BIN}/busybox 
	${BIN}/bash 
	${BIN}/nano
	${USR_BIN}/vim"

# Files related to Bash
BASH_FILES="
	${ETC}/bash/bashrc
	${ETC}/DIR_COLORS"

NANO_FILES="${ETC}/nanorc"

VIM_FILES="${ETC}/vim/vimrc"
