# OBS PTZ Camera Control Panel
I recently bought a Foscam FI9936P IP camera to use for streaming to Youtube with OBS. Using the gstreamer library I managed to capture the FHD stream correctly with low latency (details below). Next challenge was to control the pan, tilt, zoom and presets from OBS. The camera supports control through cgi commands, so the most simple way to get custom buttons in OBS seems to be a Custom Browser Dock. So I started off with a simple local .html file with javascript to send the commmands to the camera. Unfortunately the browser refused to connect to the camera due to Cross Origin Request Blocking. This was solved by runningn a local webserver using python that serves the Custom Browser Doc page and forwards the cgi commands to the camera. The final scripts work fine with the Foscam FI9936P camera and might run out-of-the-box with other foscam IP camera models as well. Support for other brand IP cameras can be added by writing an .html file with the correct cgi commands.

# PTZControlServer.py
The PTZControlServer.py python script implements the local webserver. To get it running, install python and start the server with the commandline 'python PZTControlServer.py'. If the server starts correctly, 
```C:\home\Kees\git\OBS_PTZ_Camera_Control_Panel>python PTZControlServer.py
PTZControlServer started http://localhost:8081
```
