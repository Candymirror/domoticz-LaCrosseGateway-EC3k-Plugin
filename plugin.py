# LaCrosseGateway Python Plugin for Domoticz
#
# Authors: RvdVeen
#
# Based on
#
# https://wiki.fhem.de/wiki/LaCrosseGateway_V1.x
# https://github.com/Innovatone/python-lacrossegateway/blob/master/pylacrossegateway/lacrossegateway.py
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA
"""
<plugin key="LGW" name="LaCrosseGateway" author="RvdVeen" version="0.1">
    <description>
        <h2>Domoticz LaCrosseGateway Plugin</h2><br/>
        <h3>Features</h3>
        <ul style="list-style-type:square">
            <li>Domoticz plugin implementation for decoding ec3k messages received by a LaCrosseGateway</li>
            <li>Decoding for other devices is not tested and may require setting the LGW in another mode</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="IP Address" width="200px" required="true"/>
        <param field="Port" label="Port" width="30px" required="true" default="81"/>
        <param field="Mode1" label="LGW initCommand" width="200px" required="true" default="20000#1r">
            <description><h3>LGW initCommand</h3>For example enter "20000#1r" below to set the first rfm69 to 20000kbps, to use it with an EC3k. See https://wiki.fhem.de/wiki/LaCrosseGateway_V1.x or http://"lgw-ip"/help for more information.</description>
        </param>
        <param field="Mode2" label="Query interval" width="75px" required="true">
            <options>
                <option label="15 sec" value="3"/>
                <option label="30 sec" value="6"/>
                <option label="1 min" value="12" default="true"/>
                <option label="3 min" value="36"/>
                <option label="5 min" value="60"/>
                <option label="10 min" value="120"/>
                <option label="30 min" value="360"/>
                <option label="60 min" value="720"/>
            </options>
        </param>
        <param field="Mode6" label="Debug" width="150px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
#import DomoticzEx
#import DomoticzEx as Domoticz
import re
import lacrossegateway
import Domoticz

class BasePlugin:
    enabled = False
    def __init__(self):
        #self.var = 123
        return

    def onStart(self):
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

        self.websocketConn = Domoticz.Connection(Name="websocketConn", Transport="TCP/IP", 
                                               Address=Parameters["Address"], Port=Parameters["Port"])
        self.websocketConn.Connect()

    def onStop(self):
        Domoticz.Debug("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        data = Parameters["Mode1"]
        self.websocketConn.Send((data + '\r\n').encode())
        Domoticz.Log("Setting LGW radio to listen to ec3k")

    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")
        Domoticz.Debug(Data)
        device = lacrossegateway.parse(Data)
        Domoticz.Debug(device)
        if device[0] == "EC3000":
            values = lacrossegateway.decodeEC3k(device[1])
            Domoticz.Debug(values)
            ec3kDeviceExists = False
            for unit in Devices:
                if Devices[unit].DeviceID == values[0]:
                    Devices[unit].Update(nValue=0, sValue=str(values[1]) + ";" + str(values[2]))
                    ec3kDeviceExists = True
                    Domoticz.Debug("EC3k device with sensorID: "+values[0]+" updated")
            if ec3kDeviceExists == False:
                Domoticz.Log("Found new EC3k device with sensorID "+values[0]+ ", trying to add Device")
                Domoticz.Device(Name="EC3k_"+values[0], DeviceID=values[0], Unit=len(Devices)+1, TypeName="kWh").Create()
        if device[0] == "Info":
            values = lacrossegateway.decodeInfo(device[1])
            Domoticz.Debug(values)
        if device[0] == "LaCrosseWS":
            values = lacrossegateway.decodeLaCrosseWS(device[1])
            Domoticz.Debug(values)
            LaCrosseWSExists = False
            for unit in Devices:
                if Devices[unit].DeviceID == str(values[0]):
                    Devices[unit].Update(nValue=0, sValue=str(values[1]) + ";" + str(values[2]) + ";" + str(values[3]))
                    LaCrosseWSExists = True
                    Domoticz.Debug("LaCrosseWS device with sensorID: "+str(values[0])+" updated")
            if LaCrosseWSExists == False:
                Domoticz.Log("Found new  device with sensorID "+str(values[0])+ ", trying to add Device")
                Domoticz.Device(Name="WS"+str(values[0]), DeviceID=str(values[0]), Unit=len(Devices)+1, TypeName="Temp+Hum").Create()

    def onCommand(self, DeviceID, Unit, Command, Level, Color):
        Domoticz.Debug("onCommand called for Device " + str(DeviceID) + " Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(DeviceID, Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(DeviceID, Unit, Command, Level, Color)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for DeviceName in Devices:
        Device = Devices[DeviceName]
        Domoticz.Debug("Device ID:       '" + str(Device.DeviceID) + "'")
        Domoticz.Debug("--->Unit Count:      '" + str(len(Device.Units)) + "'")
        for UnitNo in Device.Units:
            Unit = Device.Units[UnitNo]
            Domoticz.Debug("--->Unit:           " + str(UnitNo))
            Domoticz.Debug("--->Unit Name:     '" + Unit.Name + "'")
            Domoticz.Debug("--->Unit nValue:    " + str(Unit.nValue))
            Domoticz.Debug("--->Unit sValue:   '" + Unit.sValue + "'")
            Domoticz.Debug("--->Unit LastLevel: " + str(Unit.LastLevel))
    return
