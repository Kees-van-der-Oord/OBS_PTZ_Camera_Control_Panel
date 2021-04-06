# PTZControlServer.py
# Python script that serves a html page for an OBS Custom Browser Dock to control 
# the pan, tilt, zoom and presets of a Foscam PTZ camera (and possible other brands as well)
# usage: start the script with the server port and the URL and password of the camera
# python PTZControlServer -port 8081 -url http://192.168.2.100:88 -pwd <password>
# in OBS define a custom browser dock with the address http://localhost:8081
#
# to support multiple cameras, you can start the server without url and pwd arguments
# and specify them in the browser dock url: http://localhost:8081?url=http://192.168.2.100:88&pwd=<password>
#
# by default the index page 'foscam.html' is served (-type foscam)
# to implement other camera types, create a page <model>.html with the communication details of the camera
# and start the server with the -type <model> argument
#
# tested with a Foscam FI9936P camera
#
# Author: Kees van der Oord <Kees.van.der.Oord@inter.nl.net>
# Repository: https://github.com/Kees-van-der-Oord/OBS_PTZ_Camera_Control_Panel 
# Version: 0.2

import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
import threading
from urllib.parse import urlparse, parse_qs
import requests

# parameters of the server
host_name = "localhost"
server_port = 8081

# parameters for the camera
camera_url = "http://192.168.2.100:88"
camera_type = "foscam"
camera_params = {'usr':'admin','pwd':'<passsword>'}

class PTZControlServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global camera_url, camera_type, camera_params 
        parsed_path = urlparse(self.path)
        parsed_query = parse_qs(parsed_path.query)
        # serve index.html if no path is mentioned
        #print("parsed_path: ",parsed_path.path);
        if parsed_path.path == "/" or parsed_path == "/index.html" :
            #print(parsed_query);
            # type param specifies the camera type
            type = camera_type;
            if "type" in parsed_query:
                type = parsed_query["type"][0];
                del parsed_query["type"]
            #print("type: ",type);
            # the remaining parameters will always be passed (usr,pwd, ...)
            all_params = camera_params;
            all_params.update(parsed_query)
            #print("params: ", params);
            content = open(camera_type + ".html", 'rb').read()
            if content:
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content)
                return
            self.send_response(404)
            return
            
        # forward the query to the camera
        url = camera_url;
        if "url" in parsed_query:
            url = parsed_query["url"][0];
            #print("url: ",url);
            del parsed_query["url"]
        all_params = camera_params;
        all_params.update(parsed_query);
        #print("url: ", url + parsed_path.path)
        #print("params: ", all_params)
        response = requests.get(
            url + parsed_path.path,
            params=all_params,
        )
        self.send_response(response.status_code)
        for name in response.headers:
            self.send_header(name,response.headers[name])
        self.end_headers()
        if response.status_code == 200:
            self.wfile.write(response.content)
            #print(response.content)
 
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
 
if __name__ == "__main__":
    argc = len(sys.argv)
    argi = 1
    while argi < argc:
        if sys.argv[argi] == "-port":
            argi += 1
            if argi < argc:
                server_port = int(sys.argv[argi]);
                argi += 1
            else:
                print("no server port specified");
        if sys.argv[argi] == "-type":
            argi += 1
            if argi < argc:
                camera_type = sys.argv[argi];
                argi += 1
            else:
                print("no camera type specified");
        elif sys.argv[argi] == "-url":
            argi += 1
            if argi < argc:
                camera_url = sys.argv[argi];
                argi += 1
            else:
                print("no camera url specified");
        elif sys.argv[argi] == "-pwd":
            argi += 1
            if argi < argc:
                camera_params["pwd"] = sys.argv[argi];
                argi += 1
            else:
                print("no camera password specified");
        elif sys.argv[argi] == "-usr":
            argi += 1
            if argi < argc:
                camera_params["usr"] = sys.argv[argi];
                argi += 1
            else:
                print("no camera user name specified");
        else:
            print("usage: PTZControlServer.py [-url http://ipaddress:port] [-usr username] [-pwd password] [-type cameratype]")
            argi += 1

    webServer = ThreadedHTTPServer((host_name, server_port), PTZControlServer)
    print("PTZControlServer started http://%s:%s for %s camera %s" % (host_name, server_port, camera_type, camera_url))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("PTZControlServer stopped for %s camera %s." % (camera_type, camera_url))