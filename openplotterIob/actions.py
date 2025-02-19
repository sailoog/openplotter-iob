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

import sys, os, subprocess, serial
from openplotterSettings import language
import paho.mqtt.client as mqtt

class Actions:
	def __init__(self,conf,currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-iob',currentLanguage)
		if self.conf.get('GENERAL', 'debug') == 'yes': self.debug = True
		else: self.debug = False
		self.available = []

		self.available.append({'ID':'mqtt','name':_('MQTT: publish a message in topic mqtt/data/#'),"module": "openplotterIob",'data':True,'default':'topic=mqtt/data/#\npayload=xxx\nqos=0\nretain=no','help':_('Replace # with a path and xxx with a text or number.')+' qos=0|1|2. retain=no|yes'})

	def run(self,action,data):
		if action == 'mqtt': 
			try:
				broker_address = ''
				broker_port = ''
				username = ''
				password = ''
				topic = ''
				message = ''
				qos = 0
				retain = False
				broker_address = self.conf.get('IOB', 'broker')
				broker_port = int(self.conf.get('IOB', 'port'))
				username = self.conf.get('IOB', 'user')
				password = self.conf.get('IOB', 'pass')
				lines = data.split('\n')
				for i in lines:
					line = i.split('=')
					if line[0].strip() == 'topic': topic = line[1].strip()
					if line[0].strip() == 'payload': message = line[1].strip()
					if line[0].strip() == 'qos':
						try: qos = int(line[1].strip())
						except: pass
					if line[0].strip() == 'retain':
						if line[1].strip() == 'yes': retain = True
				sys.stdout.flush()
				if broker_address and broker_port and username and password and topic and message:
					client = mqtt.Client()
					client.username_pw_set(username, password)
					client.connect(broker_address, broker_port, 60)
					client.publish(topic, message, qos, retain)
					client.disconnect()
					subprocess.Popen(['set-notification','notifications.'+topic.replace("/","."),'normal', message])
				else:
					if self.debug: 
						print('Error publishing MQTT message: wrong data')
						sys.stdout.flush()
			except Exception as e: 
				if self.debug: 
					print('Error publishing MQTT message: '+str(e))
					sys.stdout.flush()
