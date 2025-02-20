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

import os, sys, subprocess
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from .version import version

def main():
	conf2 = conf.Conf()
	currentdir = os.path.dirname(os.path.abspath(__file__))
	currentLanguage = conf2.get('GENERAL', 'lang')
	hostID = conf2.get('GENERAL', 'hostID')
	package = 'openplotter-iob'
	language.Language(currentdir, package, currentLanguage)
	platform2 = platform.Platform()

	print(_('Installing python packages...'))
	try:
		if hostID != 'ubuntu': subprocess.call(['pip3', 'install', 'paho-mqtt', '-U', '--break-system-packages'])
		else: subprocess.call(['pip3', 'install', 'paho-mqtt', '-U'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Creating services...'))
	try:
		fo = open('/etc/systemd/system/openplotter-iob-read.service', "w")
		fo.write( '[Service]\nEnvironment=OPrescue=0\nEnvironmentFile=-/boot/firmware/config.txt\nExecStart=openplotter-iob-read $OPrescue\nUser='+conf2.user+'\nRestart=always\nRestartSec=3\n\n[Install]\nWantedBy=local-fs.target')
		fo.close()
		subprocess.call(['systemctl', 'daemon-reload'])
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

	print(_('Setting version...'))
	try:
		conf2.set('APPS', 'iob', version)
		print(_('DONE'))
	except Exception as e: print(_('FAILED: ')+str(e))

if __name__ == '__main__':
	main()