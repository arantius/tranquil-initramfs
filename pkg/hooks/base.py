"""
Copyright 2012-2014 Jonathan Vasquez <jvasquez1011@gmail.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

	http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from pkg.libs.toolkit import Toolkit

tools = Toolkit()

class Base(object):
	# Set the kmod path for this system
	# Funtoo = /sbin/kmod; Gentoo = /bin/kmod
	kmod_path = tools.find_prog("kmod")

	files = [
		# sys-apps/busybox
		"/bin/busybox",

		# sys-apps/kmod
		kmod_path,

		# app-shells/bash
		"/bin/bash",
		"/etc/bash/bashrc",
		"/etc/DIR_COLORS",
		"/etc/profile",

		# sys-apps/grep
		"/bin/egrep",
		"/bin/fgrep",
		"/bin/grep",
	]

	kmod_links = [ "depmod", "insmod", "lsmod",
	               "modinfo", "modprobe", "rmmod" ]
