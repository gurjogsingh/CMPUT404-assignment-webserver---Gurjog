#  coding: utf-8 
from email.charset import BASE64
from encodings import utf_8
import socketserver, time, sys, socket, http, datetime, os, mimetypes
import pathlib
from pathlib import Path
from http import HTTPStatus

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/

HOST, PORT, BUFFER_SIZE = "127.0.0.1", 8080, 1024
BASEURL = "http://127.0.0.1:8080"

class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
       
        self.data = self.request.recv(BUFFER_SIZE).strip()

        self.breaking_request()
        self.client_address
        #print ("Got a request of: %s\n" % self.data)

        self.sending_to_terminal()

       


    def sending_to_terminal(self):
        #how to print current datetime https://www.w3resource.com/python-exercises/python-basic-exercise-3.php
        now = datetime.datetime.now()
        datetime_string = now.strftime("%d/%b/%Y %H:%M:%S")

        if self.code == 404:
            print("{0} - - [{1}] code: 404, message: File Not Found".format(self.client_address[0], datetime_string))
            print("{0} - - [{4}] \"{1} {2} {3}\" {5} -".format(self.client_address[0], self.method, self.path, self.protocol, datetime_string, self.code))## look at what the dash is
        elif self.code == 405:
            print("{0} - - [{1}] code: 405, message: Method Not Allowed".format(self.client_address[0], datetime_string))
        else:
            print("{0} - - [{4}] \"{1} {2} {3}\" {5} -".format(self.client_address[0], self.method, self.path, self.protocol, datetime_string, self.code))## look at what the dash is
        


    def breaking_request(self):
        #self.method = "GET"
        #self.protocol = "HTTP/1.1"
        #self.path = "/"
        self.code = 000 #default
        data_str = str(self.data,'utf_8')
        
        stripped_request_header = data_str.split('\r\n', 1)[0]
        stripped_request_header = stripped_request_header.split()
        self.method = stripped_request_header[0]
        self.path = stripped_request_header[1]
        self.protocol = stripped_request_header[2]

        if self.method != "GET":
            self.code = 405
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed text/html\r\n", 'utf-8'))
            self.request.sendall(bytearray("Allow: GET\r\n\r\n", 'utf-8'))
            #self.request.close()
            return
        
        self.process_data()
        
    def process_data(self):
        #get path and use path to send file 
        #has to be /www/path
        default_path = str(os.getcwd()) + "/www"
        
        """ if '..' in self.path:
            print(self.path)
            self.path = os.path.abspath(self.path)
            print(os.path.abspath(self.path)) """
            
            #https://docs.python.org/3/library/os.path.html#os.path.abspath 


        """
        so whats happening.
        since abspath function gets abs path, it removes the / at the end of the path after it is processed.
        now some our paths (as per the requirements) need this / for different purposes
        depending on whether / is in the orig path or not, / is then added on to the processed abs path
        
        """

        if self.path[-1] != '/':
            print(self.path)
            self.path = os.path.abspath(self.path)
            print(os.path.abspath(self.path))
            #https://docs.python.org/3/library/os.path.html#os.path.abspath
            print("############# orig path: ", self.path)
            result = self.path.split(".")
            print("############# result: ", result)
            if len(result) == 1:
                self.code = 301
                self.path = self.path + '/'
                print("########## final path: ", self.path)


  
        if self.path[-1] == '/':
            print(self.path)
            self.path = os.path.abspath(self.path) + '/'
            print(os.path.abspath(self.path))
            #https://docs.python.org/3/library/os.path.html#os.path.abspath
            try:
                f = open(default_path + self.path + "index.html")
                self.content_type = mimetypes.guess_type(default_path + self.path + "index.html")
                if self.code != 301:
                    self.code = 200
            except:
                self.code = 404
                if self.code == 404:
                    self.page_not_found_error()
                    return
                else:
                    return
                #self.request.sendall(bytearray("Path Not Found\r\n", 'utf-8'))
                
        else:
            try:
                f = open(default_path + self.path)
                self.content_type = mimetypes.guess_type(default_path + self.path)
                self.code = 200
                
            except:
                self.code = 404
                if self.code == 404:
                    self.page_not_found_error()
                    return
                else:
                    return
                #self.request.sendall(bytearray("Path Not Found\r\n", 'utf-8'))
        
        
        output_data = f.read()
        self.file_length = len(output_data)
        self.creating_headers()
        self.request.sendall(bytearray(output_data, 'utf-8'))
        
    def creating_headers(self):
        #depending on code status, headers are sent
    
        self.message = None
        if self.code == 200:
            #< HTTP/1.0 200 OK
            #< Server: SimpleHTTP/0.6 Python/3.7.3
            #< Date: Thu, 20 Jan 2022 23:34:25 GMT
            #< Content-type: text/html
            #< Content-Length: 470
             #< Last-Modified: Thu, 20 Jan 2022 00:24:14 GMT
            self.message = "OK"
            self.request.send(bytearray("{0} {1} {2}\r\n".format(self.protocol, self.code, self.message), 'utf-8'))
            self.request.send(bytearray("Server: \r\n", 'utf-8'))
            now = datetime.datetime.now()
            datetime_string = now.strftime("%a, %d %b %Y %H:%M:%S")
            self.request.send(bytearray("Date: {0}\r\n".format(datetime_string), 'utf-8'))
            self.request.send(bytearray("Connection: close \r\n", 'utf-8'))
            self.request.send(bytearray("Content-type: {0}\r\n".format(self.content_type[0]), 'utf-8'))
            self.request.send(bytearray("Content-Length: {0}\r\n".format(self.file_length), 'utf-8'))
            self.request.send(bytearray("Last-Modified: \r\n\r\n", 'utf-8'))
        
            
        elif self.code == 301:
        #< HTTP/1.0 301 Moved Permanently
        #< Server: SimpleHTTP/0.6 Python/3.7.3
        #< Date: Fri, 21 Jan 2022 05:21:33 GMT
        #< Location: /www/deep/

            self.message = "Moved Permanently"
            self.request.send(bytearray("{0} {1} {2}\r\n".format(self.protocol, self.code, self.message), 'utf-8'))
            self.request.send(bytearray("Server: \r\n", 'utf-8'))
            now = datetime.datetime.now()
            datetime_string = now.strftime("%a, %d %b %Y %H:%M:%S")
            self.request.send(bytearray("Date: {0}\r\n".format(datetime_string), 'utf-8'))
            self.request.send(bytearray("Connection: close \r\n", 'utf-8'))
            self.request.send(bytearray("Content-type: {0}\r\n".format(self.content_type[0]), 'utf-8'))
            self.request.send(bytearray("Content-Length: {0}\r\n".format(self.file_length), 'utf-8'))
            self.request.send(bytearray("Last-Modified: \r\n", 'utf-8'))
            self.request.send(bytearray("Location: {0}\r\n\r\n".format(BASEURL + self.path), 'utf-8'))

            
  
        
    def page_not_found_error(self):
        #< HTTP/1.0 404 File not found
        #< Server: SimpleHTTP/0.6 Python/3.7.3
        #< Date: Fri, 21 Jan 2022 05:19:44 GMT
        #< Connection: close
        #< Content-Type: text/html;charset=utf-8
        #< Content-Length: 469
        #< 
        #<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
                #"http://www.w3.org/TR/html4/strict.dtd">
        #<html>
            #<head>
                #<meta http-equiv="Content-Type" content="text/html;charset=utf-8">
                #<title>Error response</title>
            #</head>
            #<body>
                #<h1>Error response</h1>
                #<p>Error code: 404</p>
                #<p>Message: File not found.</p>
                #<p>Error code explanation: HTTPStatus.NOT_FOUND - Nothing matches the given URI.</p>
            #</body>
        #</html>
            html_404_code = "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.01//EN\"\r\n" \
                "\t\t\"http://www.w3.org/TR/html4/strict.dtd\">\r\n"\
                "<html>\r\n"\
                "\t<head>\r\n"\
                    "\t\t<meta http-equiv=\"Content-Type\" content=\"text/html;charset=utf-8\">\r\n"\
                    "\t\t<title>Error response</title>\r\n"\
                "\t</head>\r\n"\
                "\t<body>\r\n"\
                    "\t\t<h1>Error response</h1>\r\n"\
                    "\t\t<p>Error code: 404</p>\r\n"\
                    "\t\t<p>Message: File not found.</p>\r\n"\
                    "\t\t<p>Error code explanation: 404 - Nothing matches the given URI.</p>\r\n"\
                "\t</body>\r\n"\
            "</html>\r\n"
            self.message = "File not found"
            self.request.send(bytearray("{0} {1} {2}\r\n".format(self.protocol, self.code, self.message), 'utf-8'))
            self.request.send(bytearray("Server: \r\n", 'utf-8'))
            now = datetime.datetime.now()
            datetime_string = now.strftime("%a, %d %b %Y %H:%M:%S")
            self.request.send(bytearray("Date: {0}\r\n".format(datetime_string), 'utf-8'))
            self.request.send(bytearray("Connection: close \r\n", 'utf-8'))
            self.request.send(bytearray("Content-type: text/html;charset=utf-8\r\n", 'utf-8'))
            self.request.send(bytearray("Content-Length: {0}\r\n\r\n".format(len(html_404_code)), 'utf-8'))
            self.request.send(bytearray(html_404_code, 'utf-8'))

    



if __name__ == "__main__":
    connection = True
    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    with socketserver.TCPServer((HOST, PORT), MyWebServer) as server:
        print("Serving HTTP on {0} port {1} (http://{0}:{1}/) ...".format(HOST, PORT))
    
        #recieved_request_socket, recieved_request_addr = server.handle_request()
        #print("Connected to ", recieved_request_addr)
        #recieved_data = recieved_request_socket.recv
        #server.socket.close()

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

            



