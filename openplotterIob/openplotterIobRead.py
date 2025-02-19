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

import sys, time, requests, json, subprocess
from openplotterSettings import conf
from openplotterSettings import platform
import paho.mqtt.client as mqtt

def main():
	if sys.argv[1] != '1':
		conf2 = conf.Conf()
		platform2 = platform.Platform()
		if conf2.get('GENERAL', 'debug') == 'yes': debug = True
		else: debug = False
		try: mqttCommands = eval(conf2.get('IOB', 'commands'))
		except: mqttCommands = {}
		# MQTT broker settings
		broker_address = conf2.get('IOB', 'broker')
		try: broker_port = int(conf2.get('IOB', 'port'))
		except:
			broker_port = 1883
			if debug:
				print("Wrong port")
				sys.stdout.flush()

		username = conf2.get('IOB', 'user')
		password = conf2.get('IOB', 'pass')

		# Topics to subscribe
		topics = ["mqtt/command/+"]

		# Callback when connection is established
		def on_connect(client, userdata, flags, rc):
			if rc == 0:
				if debug:
					print("Connected to MQTT broker")
					sys.stdout.flush()
				# Subscribe to topics
				for topic in topics:
					client.subscribe(topic)
					if debug:
						print(f"Subscribed to {topic}")
						sys.stdout.flush()
			else:
				if debug:
					print(f"Connection failed with code {rc}")
					sys.stdout.flush()

		# Callback when a message is received
		def on_message(client, userdata, msg):
			if debug:
				print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
				sys.stdout.flush()
			try:
				msgTopic = msg.topic
				message = msg.payload.decode()
				if msgTopic == 'mqtt/command/getData':
					if message == 'all':
						subprocess.Popen(['set-notification','notifications.mqtt.command.getData','normal', 'all'])
						resp = requests.get(platform2.http+'localhost:'+platform2.skPort+'/signalk/v1/api/vessels/self/', verify=False)
						client.publish('mqtt/data', resp.content, 0, False)
						subprocess.Popen(['set-notification','notifications.mqtt.data.all','normal', ''])
						if debug:
							print("Sent message to topic mqtt/data: "+str(json.loads(resp.content)))
							sys.stdout.flush()
					else:
						subprocess.Popen(['set-notification','notifications.mqtt.command.getData','normal', message])
						resp = requests.get(platform2.http+'localhost:'+platform2.skPort+'/signalk/v1/api/vessels/self/'+message, verify=False)
						client.publish('mqtt/data/'+message, resp.content, 0, False)
						subprocess.Popen(['set-notification','notifications.mqtt.data.'+message.replace("/","."),'normal', str(json.loads(resp.content))])
						if debug:
							print("Sent message to topic mqtt/data/"+message+": "+str(json.loads(resp.content)))
							sys.stdout.flush()
				elif msgTopic == 'mqtt/command/getCommand':
					if message == 'all':
						subprocess.Popen(['set-notification','notifications.mqtt.command.getCommand','normal', 'all'])
						data = []
						for i in mqttCommands:
							data.append(i)
						if data:
							client.publish('mqtt/data/command', str(data), 0, False)
							subprocess.Popen(['set-notification','notifications.mqtt.data.command.all','normal', str(data)])
						if debug:
							print("Sent message to topic mqtt/data/command: "+str(data))
							sys.stdout.flush()
					else:
						subprocess.Popen(['set-notification','notifications.mqtt.command.getCommand','normal', message])
						data = ""
						if message in mqttCommands:
							data = mqttCommands[message]['description'].replace('"', "'")
						if data:
							client.publish('mqtt/data/command', data, 0, False)
							subprocess.Popen(['set-notification','notifications.mqtt.data.command.'+message,'normal', data])
						if debug:
							print("Sent message to topic mqtt/data/command: "+data)
							sys.stdout.flush()
				else: #'mqtt/command/+'
					command = ''
					state = 'normal'
					method = ''
					data = msgTopic.split('/')
					if data[0] == 'mqtt' and data[1] == 'command' and len(data) == 3: command = data[2]
					if command:
						if command in mqttCommands: 
							state = mqttCommands[command]['state']
							if 'visual' in mqttCommands[command]['method']: method += ' -v'
							if 'sound' in mqttCommands[command]['method']: method += ' -s'
						subprocess.Popen(['set-notification', method, 'notifications.mqtt.command.'+command, state, message])
			except Exception as e:
				if debug:
					print(f"Error handling the message: {e}")
					sys.stdout.flush()

		# Callback when disconnected
		def on_disconnect(client, userdata, rc):
			if debug:
				print("Disconnected from MQTT broker")
				sys.stdout.flush()
			reconnect()

		# Function to handle reconnection
		def reconnect():
			while True:
				try:
					client.reconnect()
					break
				except Exception as e:
					if debug:
						print(f"Reconnection failed: {e}")
						sys.stdout.flush()
					time.sleep(5)  # Wait for 5 seconds before trying again

		# Create MQTT client instance
		client = mqtt.Client()

		# Set username and password
		client.username_pw_set(username, password)

		# Set callbacks
		client.on_connect = on_connect
		client.on_message = on_message
		client.on_disconnect = on_disconnect

		# Connect to the broker
		try:
			client.connect(broker_address, broker_port)
		except Exception as e:
			if debug:
				print(f"Initial connection failed: {e}")
				sys.stdout.flush()
			reconnect()

		# Start the loop
		client.loop_forever()



if __name__ == '__main__':
	main()