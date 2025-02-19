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

import wx, os, webbrowser, subprocess, time, sys
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
import paho.mqtt.client as mqtt
from .version import version

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.conf_folder = self.conf.conf_folder
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-iob',self.currentLanguage)

		wx.Frame.__init__(self, None, title='IoB '+version, size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/openplotter-iob.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		if not self.platform.isInstalled('openplotter-doc'): self.toolbar1.EnableTool(101,False)
		toolSettings = self.toolbar1.AddTool(102, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.iob = wx.Panel(self.notebook)
		self.telegram = wx.Panel(self.notebook)
		self.lora = wx.Panel(self.notebook)
		self.notebook.AddPage(self.iob, 'MQTT')
		self.notebook.AddPage(self.telegram, 'Telegram')
		self.notebook.AddPage(self.lora, 'LoRaWAN')
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/mqtt.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/telegram.png", wx.BITMAP_TYPE_PNG))
		img2 = self.il.Add(wx.Bitmap(self.currentdir+"/data/lora.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)
		self.notebook.SetPageImage(2, img2)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.pageIob()
		self.pageTelegram()
		self.pageLora()

		self.onRead()

		maxi = self.conf.get('GENERAL', 'maximize')
		if maxi == '1': self.Maximize()

		self.Centre()

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0)) 

	def onTabChange(self, event):
		try:
			self.SetStatusText('')
		except:pass

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/iob/iob_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event=0): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def onRead(self):
		self.onListMqttDeselected()
		self.listMqtt.DeleteAllItems()
		try: self.mqttCommands = eval(self.conf.get('IOB', 'commands'))
		except: self.mqttCommands = {}
		if not 'getData' in self.mqttCommands or not 'getCommand' in self.mqttCommands:
			getData = {'description': _('Send "all" to topic "mqtt/command/getData" and you will receive a json message in topic "mqtt/data" with all the data for the boat at that moment. If you send a Signal K key instead of "all", such as "environment/inside/temperature", you will receive a message with only that data in topic "mqtt/data/environment/inside/temperature": "{"value":293.45,"$source": "OpenPlotter.I2C.BME680/688", "timestamp": "2025-01-31T18:55:24.124Z"}". If you are only interested in the value of that Signal K key, send "environment/inside/temperature/value" and you will receive "293.45" in topic "mqtt/data/environment/inside/temperature/value"'), 'state': 'normal', 'method': []}
			getCommand = {'description': _('Send "all" to topic "mqtt/command/getCommand" and you will receive the list of all defined commands in topic "mqtt/data/command": ["getData","getCommand"...]. If you send a command instead of "all", such as "getData", you will receive the description of that command in topic "mqtt/data/command"'), 'state': 'normal', 'method': []}
			self.mqttCommands['getData'] = getData
			self.mqttCommands['getCommand'] = getCommand
			self.conf.set('IOB', 'commands', str(self.mqttCommands))
		for i in self.mqttCommands:
			self.listMqtt.Append([i, self.mqttCommands[i]['description'],self.mqttCommands[i]['state'],str(self.mqttCommands[i]['method'])])

		self.broker.SetValue(self.conf.get('IOB', 'broker'))
		self.port.SetValue(self.conf.get('IOB', 'port'))
		self.User.SetValue(self.conf.get('IOB', 'user'))
		self.Pass.SetValue(self.conf.get('IOB', 'pass'))
		self.startup.SetValue(self.conf.get('IOB', 'startup') == '1')
		if not self.broker.GetValue(): self.broker.SetValue('mqtt.openmarine.net')
		if not self.port.GetValue(): self.port.SetValue('1883')

	def restartRead(self, startup):
		subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'start', startup])
		time.sleep(1)

	def stopRead(self, startup):
		subprocess.call([self.platform.admin, 'python3', self.currentdir+'/service.py', 'stop', startup])
		time.sleep(1)

################################################################################

	def pageIob(self):
		BrokerLabel = wx.StaticText(self.iob, label='Broker')
		self.broker = wx.TextCtrl(self.iob)
		PortLabel = wx.StaticText(self.iob, label=_('Port'))
		self.port = wx.TextCtrl(self.iob)
		UserLabel = wx.StaticText(self.iob, label=_('Username'))
		self.User = wx.TextCtrl(self.iob)
		PassLabel = wx.StaticText(self.iob, label=_('Password'))
		self.Pass = wx.TextCtrl(self.iob, style=wx.TE_PASSWORD)
		account = wx.Button(self.iob, label=_('Create an account'))
		self.Bind(wx.EVT_BUTTON, self.onAccount, account)
		self.startup = wx.CheckBox(self.iob, label=_('Connect at startup'))
		save = wx.Button(self.iob, label=_('Test connection and save'))
		self.Bind(wx.EVT_BUTTON, self.onSave, save)

		self.listMqtt = wx.ListCtrl(self.iob, -1, style=wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.LC_HRULES, size=(-1,200))
		self.listMqtt.InsertColumn(0, _('Command'), width=110)
		self.listMqtt.InsertColumn(1, _('Description'), width=400)
		self.listMqtt.InsertColumn(2, _('State'), width=90)
		self.listMqtt.InsertColumn(3, _('Method'), width=125)
		self.listMqtt.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListMqttSelected)
		self.listMqtt.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListMqttDeselected)
		self.listMqtt.SetTextColour(wx.BLACK)

		self.toolbar8 = wx.ToolBar(self.iob, style=wx.TB_VERTICAL)
		addMqtt = self.toolbar8.AddTool(801, _('Add'), wx.Bitmap(self.currentdir+"/data/add.png"))
		self.Bind(wx.EVT_TOOL, self.onAddMqtt, addMqtt)
		self.toolbar8.AddSeparator()
		toolEdit = self.toolbar8.AddTool(802, _('Edit'), wx.Bitmap(self.currentdir+"/data/edit.png"))
		self.Bind(wx.EVT_TOOL, self.onToolEdit, toolEdit)
		toolDelete = self.toolbar8.AddTool(803, _('Delete'), wx.Bitmap(self.currentdir+"/data/cancel.png"))
		self.Bind(wx.EVT_TOOL, self.onToolDelete, toolDelete)
		self.toolbar8.AddSeparator()

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.Add(BrokerLabel, 0, wx.ALL | wx.EXPAND, 5)
		hbox1.Add(self.broker, 1, wx.ALL | wx.EXPAND, 5)
		hbox1.Add(PortLabel, 0, wx.ALL | wx.EXPAND, 5)
		hbox1.Add(self.port, 0, wx.ALL | wx.EXPAND, 5)
		hbox1.Add(account, 0, wx.ALL | wx.EXPAND, 5)
		hbox1.Add(self.startup, 0, wx.ALL | wx.EXPAND, 5)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.Add(UserLabel, 0, wx.ALL | wx.EXPAND, 5)
		hbox2.Add(self.User , 1, wx.ALL | wx.EXPAND, 5)
		hbox2.Add(PassLabel, 0, wx.ALL | wx.EXPAND, 5)
		hbox2.Add(self.Pass, 1, wx.ALL | wx.EXPAND, 5)
		hbox2.Add(save, 0, wx.ALL | wx.EXPAND, 5)

		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add(self.listMqtt , 1, wx.ALL | wx.EXPAND, 0)
		hbox3.Add(self.toolbar8 , 0, wx.EXPAND, 0)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(hbox1, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(hbox2, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(hbox3, 1, wx.EXPAND, 0)
		self.iob.SetSizer(vbox)

	def onAddMqtt(self,e):
		edit = {}
		self.setMqtt(edit)

	def setMqtt(self,edit):
		dlg = editMqtt(edit,self.mqttCommands)
		res = dlg.ShowModal()
		if res == wx.ID_OK:
			command = dlg.command.GetValue()
			description = dlg.description.GetValue()
			state = dlg.state.GetValue()
			visual = dlg.visual.GetValue()
			sound = dlg.sound.GetValue()
			method = []
			if visual: method.append('visual')
			if sound: method.append('sound')
			self.mqttCommands[command] = {'description': description, 'state': state, 'method': str(method)}
			self.conf.set('IOB', 'commands', str(self.mqttCommands))
			self.onRead()
			try:
				subprocess.check_output(['systemctl', 'is-active', 'openplotter-iob-read']).decode(sys.stdin.encoding)
				self.restartRead('none')
			except: pass
		dlg.Destroy()
		
	def onToolEdit(self,e):
		selected = self.listMqtt.GetFirstSelected()
		if selected == -1: return
		command = self.listMqtt.GetItemText(selected, 0)
		description = self.listMqtt.GetItemText(selected, 1)
		state = self.listMqtt.GetItemText(selected, 2)
		method = eval(self.listMqtt.GetItemText(selected, 3))
		edit = {'command':command,'description':description,'state':state,'method':method}
		self.setMqtt(edit)

	def onToolDelete(self,e):
		selected = self.listMqtt.GetFirstSelected()
		if selected == -1: return
		command = self.listMqtt.GetItemText(selected, 0)
		if command == 'getData' or command == 'getCommand':
			wx.MessageBox(_('This command cannot be deleted.'), _('Info'), wx.OK | wx.ICON_INFORMATION)
			return
		del self.mqttCommands[command]
		self.conf.set('IOB', 'commands', str(self.mqttCommands))
		self.onRead()
		try:
			subprocess.check_output(['systemctl', 'is-active', 'openplotter-iob-read']).decode(sys.stdin.encoding)
			self.restartRead('none')
		except: pass

	def onListMqttSelected(self, e):
		self.onListMqttDeselected()
		selected = self.listMqtt.GetFirstSelected()
		if selected == -1: return
		self.toolbar8.EnableTool(802,True)
		self.toolbar8.EnableTool(803,True)

	def onListMqttDeselected(self, event=0):
		self.toolbar8.EnableTool(802,False)
		self.toolbar8.EnableTool(803,False)

	def onAccount(self,e):
		url = "https://shop.openmarine.net/login?create_account=1"
		webbrowser.open(url, new=2)

	def onSave(self,e):
		try: testport = int(self.port.GetValue())
		except:
			self.ShowStatusBarRED(_('Port must be an integer'))
			return
		self.conf.set('IOB', 'broker', self.broker.GetValue())
		self.conf.set('IOB', 'port', self.port.GetValue())
		self.conf.set('IOB', 'user', self.User.GetValue())
		self.conf.set('IOB', 'pass', self.Pass.GetValue())

		self.ShowStatusBarYELLOW(_('Testing connection...'))

		def on_connect(client, userdata, flags, rc):
			if rc == 0: 
				self.ShowStatusBarGREEN(_('Connection successful'))
				if self.startup.GetValue():
					self.conf.set('IOB', 'startup', '1')
					startup = 'enable'
				else:
					self.conf.set('IOB', 'startup', '0')
					startup = 'disable'
				self.restartRead(startup)
				return
			elif rc == 4: error = _('wrong password')
			elif rc == 5: error = _('wrong username or password')
			else: error = _('error code')+' '+str(rc)
			self.ShowStatusBarRED(_('Connection failed:')+' '+error)
			self.startup.SetValue(False)
			self.conf.set('IOB', 'startup', '0')
			self.stopRead('disable')

		client = mqtt.Client()
		client.username_pw_set(self.User.GetValue(), self.Pass.GetValue())
		client.on_connect = on_connect
		try:
			client.connect(self.broker.GetValue(), int(self.port.GetValue()))
			client.loop_start()
			time.sleep(3)
			client.loop_stop()
		except Exception as e:
			self.ShowStatusBarRED(_("Connection failed: ")+str(e))



################################################################################

	def pageTelegram(self):
		text1 = wx.StaticText(self.telegram, label='Coming soon')
		text2 = wx.StaticText(self.telegram, label='Let us know if you can help with this.')

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.AddStretchSpacer(1)
		hbox1.Add(text1, 0, wx.ALL | wx.EXPAND, 5)
		hbox1.AddStretchSpacer(1)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.AddStretchSpacer(1)
		hbox2.Add(text2, 0, wx.ALL | wx.EXPAND, 5)
		hbox2.AddStretchSpacer(1)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddStretchSpacer(1)
		vbox.Add(hbox1, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(hbox2, 0, wx.ALL | wx.EXPAND, 5)
		vbox.AddStretchSpacer(1)
		self.telegram.SetSizer(vbox)


################################################################################

	def pageLora(self):
		text1 = wx.StaticText(self.lora, label='Coming soon')
		text2 = wx.StaticText(self.lora, label='Let us know if you can help with this.')

		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		hbox1.AddStretchSpacer(1)
		hbox1.Add(text1, 0, wx.ALL | wx.EXPAND, 5)
		hbox1.AddStretchSpacer(1)

		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		hbox2.AddStretchSpacer(1)
		hbox2.Add(text2, 0, wx.ALL | wx.EXPAND, 5)
		hbox2.AddStretchSpacer(1)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.AddStretchSpacer(1)
		vbox.Add(hbox1, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(hbox2, 0, wx.ALL | wx.EXPAND, 5)
		vbox.AddStretchSpacer(1)
		self.lora.SetSizer(vbox)

################################################################################

class editMqtt(wx.Dialog):

	def __init__(self,edit,mqttCommands):
		if edit: title = _('Editing MQTT command')
		else: title = _('Adding MQTT command')

		self.mqttCommands = mqttCommands
		self.edit = edit
		self.conf = conf.Conf()
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		if self.conf.get('GENERAL', 'debug') == 'yes': self.debug = True
		else: self.debug = False

		wx.Dialog.__init__(self, None, title=title, size=(500, 350))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		panel = wx.Panel(self)

		commandLabel= wx.StaticText(panel, label = _('Command:'))
		self.command = wx.TextCtrl(panel,size=(-1, 25))
		if edit: self.command.SetValue(edit['command'])

		descriptionLabel= wx.StaticText(panel, label = _('Description:'))
		self.description = wx.TextCtrl(panel, style=wx.TE_MULTILINE)
		if edit: self.description.SetValue(edit['description'])

		stateLabel= wx.StaticText(panel, label = _('State:'))
		self.state = wx.ComboBox(panel, choices = ['nominal','normal','alert','warn','alarm','emergency'], style=wx.CB_READONLY)
		if edit: self.state.SetValue(edit['state'])
		else: self.state.SetSelection(0)

		methodLabel = wx.StaticText(panel, label = _('Method:'))
		self.visual = wx.CheckBox(panel, label='visual')
		self.sound = wx.CheckBox(panel, label='sound')
		if edit:
			if 'visual' in edit['method']: self.visual.SetValue(True)
			if 'sound' in edit['method']: self.sound.SetValue(True)

		cancelBtn = wx.Button(panel, wx.ID_CANCEL)
		okBtn = wx.Button(panel, wx.ID_OK)
		okBtn.Bind(wx.EVT_BUTTON, self.ok)

		h1 = wx.BoxSizer(wx.HORIZONTAL)
		h1.Add(commandLabel, 0, wx.ALL | wx.EXPAND, 5)
		h1.Add(self.command, 1, wx.ALL | wx.EXPAND, 5)

		h2 = wx.BoxSizer(wx.HORIZONTAL)
		h2.Add(stateLabel, 0, wx.ALL | wx.EXPAND, 5)
		h2.Add(self.state, 0, wx.ALL | wx.EXPAND, 5)
		h2.AddSpacer(10)
		h2.Add(methodLabel, 0, wx.ALL | wx.EXPAND, 5)
		h2.Add(self.visual, 0, wx.ALL | wx.EXPAND, 5)
		h2.Add(self.sound, 0, wx.ALL | wx.EXPAND, 5)

		actionbox = wx.BoxSizer(wx.HORIZONTAL)
		actionbox.AddStretchSpacer(1)
		actionbox.Add(cancelBtn, 0, wx.LEFT | wx.EXPAND, 10)
		actionbox.Add(okBtn, 0, wx.LEFT | wx.EXPAND, 10)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(h1, 0, wx.ALL | wx.EXPAND, 0)
		vbox.Add(descriptionLabel, 0, wx.ALL | wx.EXPAND, 5)
		vbox.Add(self.description, 1, wx.ALL | wx.EXPAND, 5)
		vbox.Add(h2, 0, wx.ALL | wx.EXPAND, 0)
		vbox.Add(actionbox, 0, wx.ALL | wx.EXPAND, 10)

		panel.SetSizer(vbox)

		self.Centre() 

	def ok(self,e):
		if self.edit:
			if self.command.GetValue() == 'getData' or self.command.GetValue() == 'getCommand':
				wx.MessageBox(_('This command cannot be edited.'), _('Info'), wx.OK | wx.ICON_INFORMATION)
				return
		if self.edit and self.edit['command'] != self.command.GetValue() or not self.edit:
			if self.command.GetValue() in self.mqttCommands:
				wx.MessageBox(_('This command already exists.'), _('Info'), wx.OK | wx.ICON_INFORMATION)
				return
		self.EndModal(wx.ID_OK)

################################################################################

def main():
	try:
		platform2 = platform.Platform()
		if not platform2.postInstall(version,'iob'):
			subprocess.Popen(['openplotterPostInstall', platform2.admin+' iobPostInstall'])
	except: pass

	app = wx.App()
	MyFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
