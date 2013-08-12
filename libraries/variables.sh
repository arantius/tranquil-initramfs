# Copyright (C) 2012, 2013 Jonathan Vasquez <jvasquez1011@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

# Application Info
NAME="Bliss Initramfs Creator"
AUTHOR="Jonathan Vasquez"
EMAIL="jvasquez1011@gmail.com"
CONTACT="${AUTHOR} <${EMAIL}>"
VERSION="2.1.0"
LICENSE="MPL 2.0"

# Parameters and Locations
H="$(pwd)"                      # Home
T="${H}/temp"                   # Temporary Directory

# Plugins Directory
PLUGINS="${H}/plugins"

BIN="/bin"
SBIN="/sbin"
LIB="/lib"
LIB64="/lib64"
MAN="/usr/share/man"
UDEV="${LIB64}/udev"
ETC="/etc"

# Directories in /usr
UBIN="/usr/bin"
USBIN="/usr/sbin"
ULIB="/usr/lib"
USHARE="/usr/share"
UEXEC="/usr/libexec"

# Paths in Temp (Local)
LBIN="${T}/${BIN}"
LSBIN="${T}/${SBIN}"
LLIB="${T}/${LIB}"
LLIB64="${T}/${LIB64}"
LMAN="${T}/${MAN}"
LUDEV="${T}/${UDEV}"
LETC="${T}/${ETC}"
LUSHARE="${T}/${USHARE}"

# Get CPU Architecture
ARCH="$(uname -m)"

# Preliminary binaries needed for the success of creating the initrd
# but that are not needed to be placed inside the initrd
PREL_BIN="/bin/cpio"

# Directories to create when generating the initramfs structure
CDIRS="
	${T}/bin \
	${T}/sbin \
	${T}/usr/bin \
        ${T}/proc \
	${T}/sys \
	${T}/dev \
	${T}/etc \
	${T}/mnt/root \
	${T}/libraries \
	${T}/lib"
