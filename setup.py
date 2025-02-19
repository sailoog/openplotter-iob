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

from setuptools import setup
from openplotterIob import version

setup (
	name = 'openplotterIob',
	version = version.version,
	description = 'OpenPlotter app to manage your boat remotely',
	license = 'GPLv3',
	author="Sailoog",
	author_email='info@sailoog.com',
	url='https://github.com/openplotter/openplotter-iob',
	packages=['openplotterIob'],
	classifiers = ['Natural Language :: English',
	'Operating System :: POSIX :: Linux',
	'Programming Language :: Python :: 3'],
	include_package_data=True,
	entry_points={'console_scripts': ['openplotter-iob=openplotterIob.openplotterIob:main','iobPostInstall=openplotterIob.iobPostInstall:main','iobPreUninstall=openplotterIob.iobPreUninstall:main','openplotter-iob-read=openplotterIob.openplotterIobRead:main']},
	data_files=[('share/applications', ['openplotterIob/data/openplotter-iob.desktop']),('share/pixmaps', ['openplotterIob/data/openplotter-iob.png']),],
	)
