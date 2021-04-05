import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
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
            #print("index.html");
            #print(parsed_query);
            # url param specifies the camera URL
            # type param specifies the camera type
            if "type" in parsed_query:
                camera_type = parsed_query["type"][0];
                #print("camera_type: ",camera_type);
                del parsed_query["type"]
            if "url" in parsed_query:
                camera_url = parsed_query["url"][0];
                #print("camera_url: ",camera_url);
                del parsed_query["url"]
            # the remaining parameters will always be passed (usr,pwd, ...)
            camera_params.update(parsed_query)
            #print("camera_params: ", camera_params);
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            content = open(camera_type + ".html", 'rb').read()
            self.wfile.write(content)
            return
            
        # forward the query to the camera
        all_params = camera_params;
        all_params.update(parsed_query);
        #print(camera_url + parsed_path.path)
        #print(all_params)
        response = requests.get(
            camera_url + parsed_path.path,
            params=all_params,
        )
        self.send_response(response.status_code)
        for name in response.headers:
            self.send_header(name,response.headers[name])
        self.end_headers()
        self.wfile.write(response.content)
        #print(response.content)
     
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

    webServer = HTTPServer((host_name, server_port), PTZControlServer)
    print("PTZControlServer started http://%s:%s for %s camera %s" % (host_name, server_port, camera_type, camera_url))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("PTZControlServer stopped for %s camera %s." % (camera_type, camera_url))