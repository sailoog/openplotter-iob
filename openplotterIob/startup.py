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

import time, os, subprocess, sys
from openplotterSettings import language
import paho.mqtt.client as mqtt

class Start():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-iob',currentLanguage)
		
		self.initialMessage = ('')

	def start(self):
		green = ''
		black = ''
		red = ''

		return {'green': green,'black': black,'red': red}

class Check():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-iob',currentLanguage)
		self.green = ''
		self.black = ''
		self.red = ''
		self.initialMessage = _('Checking IoB...')

	def check(self):
		try:
			def on_connect(client, userdata, flags, rc):
				if rc == 0: self.error = False
				else: self.error = True

			broker_address = self.conf.get('IOB', 'broker')
			broker_port = self.conf.get('IOB', 'port')
			username = self.conf.get('IOB', 'user')
			password = self.conf.get('IOB', 'pass')
			startup = self.conf.get('IOB', 'startup')

			if broker_address and broker_port and username and password and startup == '1':
				client = mqtt.Client()
				client.username_pw_set(username, password)
				client.on_connect = on_connect
				client.connect(broker_address, int(broker_port))
				client.loop_start()
				time.sleep(3)
				client.loop_stop()

				if self.error:
					msg = _('Error connecting to MQTT server')
					if self.red: self.red += '\n   '+msg
					else: self.red = msg
					#service
					try:
						subprocess.check_output(['systemctl', 'is-active', 'openplotter-iob-read.service']).decode(sys.stdin.encoding)
						msg = _('service running')
						if self.red: self.red += '\n   '+msg
						else: self.red = msg
					except: 
						msg = _('service not running')
						if not self.black: self.black = msg
						else: self.black+= ' | '+msg
				else:
					msg = _('MQTT server connected')
					if not self.green: self.green = msg
					else: self.green+= ' | '+msg
					#service
					try:
						subprocess.check_output(['systemctl', 'is-active', 'openplotter-iob-read.service']).decode(sys.stdin.encoding)
						msg = _('service running')
						if not self.green: self.green = msg
						else: self.green+= ' | '+msg
					except: 
						msg = _('service not running')
						if self.red: self.red += '\n   '+msg
						else: self.red = msg

			else:
				msg = _('Connect at startup disabled')
				if not self.black: self.black = msg
				else: self.black+= ' | '+msg
				#service
				try:
					subprocess.check_output(['systemctl', 'is-active', 'openplotter-iob-read.service']).decode(sys.stdin.encoding)
					msg = _('service running')
					if self.red: self.red += '\n   '+msg
					else: self.red = msg
				except: 
					msg = _('service not running')
					if not self.black: self.black = msg
					else: self.black+= ' | '+msg

		except Exception as e:
			msg = _('Error connecting to MQTT server:')+' '+str(e)
			if self.red: self.red += '\n   '+msg
			else: self.red = msg

		return {'green': self.green,'black': self.black,'red': self.red}

