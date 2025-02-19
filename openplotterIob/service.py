#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2025 by Sailoog <https://github.com/openplotter/openplotter-iob>
#                  
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import sys, subprocess

if sys.argv[1]=='start':
	subprocess.call(['systemctl', 'restart', 'openplotter-iob-read.service'])
elif sys.argv[1]=='stop':
	subprocess.call(['systemctl', 'stop', 'openplotter-iob-read.service'])

if sys.argv[2]=='enable':
	subprocess.call(['systemctl', 'enable', 'openplotter-iob-read.service'])
elif sys.argv[2]=='disable':
	subprocess.call(['systemctl', 'disable', 'openplotter-iob-read.service'])