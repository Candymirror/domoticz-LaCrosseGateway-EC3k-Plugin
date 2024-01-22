# domoticz-LaCrosseGateway-EC3k-Plugin
Domoticz Plugin for EC3k (La Crosse energy count 3000) devices Through FHEM LaCrosseGateway

Disclamer!
Here's my first attempt at writing a Domoticz plugin. I'm not a python programmer nor a programmer at all. So this is not the best code around.
All is based upon the work of:
Innovatone: https://github.com/Innovatone/python-lacrossegateway
Fhem La Crosse Gateway: FHEM/36_LaCrosseGateway.pm and FHEM/36_EC3000.pm
Lacrossegateway: https://wiki.fhem.de/wiki/LaCrosseGateway_V1.x

I only added code to decode the EC3k (Energy Count 3000 or Netbsem4) with help from the FHEM LGW source code and the plugincode for the Domoticz integration.

To use this plugin you'll need a La Crosse Gateway. I build mine myself. 

Put these files in a new folder in your Domoticz plugin folder, restart domoticz.

Once restarted go to Hardware and choose type LaCrosseGateway, fill in the IP address of the LGW and port (81 or 82). Give it a name and all plugged EC3k devices should be found if you allow Domoticz to automatically accept new Hardware/sensors
