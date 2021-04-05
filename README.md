# OBS PTZ Camera Control Panel
I recently bought a Foscam FI9936P IP camera to use for streaming to Youtube with OBS. Using the gstreamer library I managed to capture the FHD stream correctly with low latency (details below). Next challenge was to control the pan, tilt, zoom and presets from OBS. The camera supports control through cgi commands, so the most simple way to get custom buttons in OBS seems to be a Custom Browser Dock. So I started off with a simple local .html file with javascript to send the commmands to the camera. Unfortunately the browser refused to connect to the camera due to Cross Origin Request Blocking. This was solved by runningn a local webserver using python that serves the Custom Browser Doc page and forwards the cgi commands to the camera. The final scripts work fine with the Foscam FI9936P camera and might run out-of-the-box with other foscam IP camera models as well. Support for other brand IP cameras can be added by writing an .html file with the correct cgi commands.

## PTZControlServer.py
The PTZControlServer.py python script implements the local webserver. To get it running, install python and start the server with the commandline 'python PZTControlServer.py'. If the server starts correctly, it should tell you that it is 'started':
```
> python PTZControlServer.py -type foscam -url http://192.168.2.100:88 -pwd PASSWORD
PTZControlServer started http://localhost:8081 for foscam camera http://192.168.2.100:88
```
If not, it is likely that port 8081 is already used by another server. Changing the server port in the .py file for a random other number will fix that.
The server accepts the following command lne parameters:
|key|value|
|--|--|
|type|the camera type (defaults to 'foscam')|
|url|url of the camera (protocol://ip-address:port)|
|usr|the name of the user (defaults to 'admin')|
|pwd|the password|

To test the server, launch your favorite browser and enter the following URL:
```
http://localhost:8081?hidestandardpresets
```

When the cgi requests to the camera succeed, the Presets list should be populated and you can use the <>^v buttons to tilt and pan the camera.\
<img src='https://raw.githubusercontent.com/Kees-van-der-Oord/OBS_PTZ_Camera_Control_Panel/main/OBS_PTZ_Camera_Control_Panel.png'>

To delete or add a preset, enter the name of the preset in the lower text field and press the + (add) or - (delete) button.

The actual .cgi commands are present in the file 'foscam.html'. When another 'type' is specified, the server will look for an .html file with that name. The javascript in the .html file uses a XMLHttpRequest to send the commands to the server. The server forwards all requests with a non-empty path to the camera.

The python webserver only supports one client. To support more cameras you have to start a server session for each camera on a different port.
