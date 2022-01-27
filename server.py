#  coding: utf-8 
import socketserver, time, os, mimetypes

# Copyright 2022 Gurjog Singh, 2013 Abram Hindle, Eddie Antonio Santos
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
        #handles the request
       
       #Used code from Lab 2 client.py (line 58-63) 
        self.data = b""
        while True:
            if self.data.find(b"\r\n\r\n") != -1:
                break
            data = self.request.recv(BUFFER_SIZE)
            self.data += data
            if self.data == b"":
                return
         
        self.data.strip()
        #self.data = self.request.recv(BUFFER_SIZE).strip()
  
        self.breaking_request()
        self.client_address
        self.sending_to_terminal()

    def sending_to_terminal(self):
        #sends messages back to terminal running server

        #how to print current GMT time https://www.askpython.com/python/examples/convert-seconds-hours-minutes (Copyright 2022 AskPython )
        datetime_string = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time()))

        if self.code == 404:
            print("{0} - - [{1}] code: 404, message: File Not Found".format(self.client_address[0], datetime_string))
            print("{0} - - [{4}] \"{1} {2} {3}\" {5} -".format(self.client_address[0], self.method, self.origpath, self.protocol, datetime_string, self.code))## look at what the dash is
        elif self.code == 405:
            print("{0} - - [{1}] code: 405, message: Method Not Allowed".format(self.client_address[0], datetime_string))
        elif self.code == 400:
            print("{0} - - [{1}] code: 400, message: Bad Request".format(self.client_address[0], datetime_string))
        else:
            print("{0} - - [{4}] \"{1} {2} {3}\" {5} -".format(self.client_address[0], self.method, self.origpath, self.protocol, datetime_string, self.code))## look at what the dash is
        


    def breaking_request(self):
        #breaks down request recieved from client

        self.code = 000 #default
        data_str = str(self.data, 'utf-8')
    
        stripped_request_header = data_str.split('\r\n', 1)[0]
        stripped_request_header = stripped_request_header.split()
        self.method = stripped_request_header[0]
        self.path = stripped_request_header[1]

        self.origpath = self.path
        self.protocol = stripped_request_header[2]
        
        if self.protocol != "HTTP/1.1":
            self.code = 400
            self.bad_request_error()
            return

        if self.method != "GET":
            self.code = 405
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed text/html\r\n", 'utf-8'))
            self.request.sendall(bytearray("Allow: GET\r\n\r\n", 'utf-8'))

            return
        
        self.process_data()
        
    def process_data(self):
        #get and resolve path and use path to send file 
        #has to be /www/path
        self.default_path = str(os.getcwd()) + "/www"
        self.updated_path = None
        
        if self.path[-1] != '/':
            #how to get absolute path from https://docs.python.org/3/library/os.path.html#os.path.abspath (Copyright 2001-2022, Python Software Foundation)
            self.path = os.path.abspath(self.path)
        
            result = self.path.split(".")
            if len(result) == 1:
                self.code = 301
                self.path = self.path + '/'

  
        if self.path[-1] == '/':
            #how to get absolute path from https://docs.python.org/3/library/os.path.html#os.path.abspath (Copyright 2001-2022, Python Software Foundation)
            self.path = os.path.abspath(self.path) + '/'
            
            try:
                self.updated_path = self.default_path + self.path + "index.html"
                f = open(self.updated_path)
                #how to use mimetype from https://docs.python.org/3/library/mimetypes.html( Copyright 2001-2022, Python Software Foundation)
                self.content_type = mimetypes.guess_type(self.updated_path)
                if self.code != 301:
                    self.code = 200
            except:
                self.code = 404
                if self.code == 404:
                    self.page_not_found_error()
                    return
                else:
                    return            
        else:
            try:
                self.updated_path = self.default_path + self.path
                f = open(self.updated_path)
                #how to use mimetype from https://docs.python.org/3/library/mimetypes.html (Copyright 2001-2022, Python Software Foundation)
                self.content_type = mimetypes.guess_type(self.updated_path)
                self.code = 200
                
            except:
                self.code = 404
                if self.code == 404:
                    self.page_not_found_error()
                    return
                else:
                    return
        
        output_data = f.read()
        self.file_length = len(output_data)
        self.creating_headers()
        self.request.sendall(bytearray(output_data, 'utf-8'))
        
    def creating_headers(self):
        #depending on accepted code status, headers are sent
    
        self.message = None
        if self.code == 200:
            self.message = "OK"
            self.request.send(bytearray("{0} {1} {2}\r\n".format(self.protocol, self.code, self.message), 'utf-8'))
            self.request.send(bytearray("Server: Gurjog's Server\r\n", 'utf-8'))
            #how to print current GMT time https://www.askpython.com/python/examples/convert-seconds-hours-minutes (Copyright 2022 AskPython )
            datetime_string = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time()))
            self.request.send(bytearray("Date: {0}\r\n".format(datetime_string), 'utf-8'))
            self.request.send(bytearray("Connection: close \r\n", 'utf-8'))
            self.request.send(bytearray("Content-type: {0}\r\n".format(self.content_type[0]), 'utf-8'))
            self.request.send(bytearray("Content-Length: {0}\r\n".format(self.file_length), 'utf-8'))
            #how to get last modified time https://www.kite.com/python/answers/how-to-get-the-last-modified-time-of-a-file-in-python (Copyright 2022 Kite)
            lastModified = time.strftime("%a, %d %b %Y %H:%M:%S GMT",(time.gmtime(os.path.getmtime(self.updated_path))))
            self.request.send(bytearray("Last-Modified: {0}\r\n\r\n".format(lastModified), 'utf-8'))
        
            
        elif self.code == 301:
 
            self.message = "Moved Permanently"
            self.request.send(bytearray("{0} {1} {2}\r\n".format(self.protocol, self.code, self.message), 'utf-8'))
            self.request.send(bytearray("Server: Gurjog's server\r\n", 'utf-8'))
            #how to print current GMT time https://www.askpython.com/python/examples/convert-seconds-hours-minutes (Copyright 2022 AskPython )
            datetime_string = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time()))
            self.request.send(bytearray("Date: {0}\r\n".format(datetime_string), 'utf-8'))
            self.request.send(bytearray("Connection: close \r\n", 'utf-8'))
            self.request.send(bytearray("Content-type: {0}\r\n".format(self.content_type[0]), 'utf-8'))
            self.request.send(bytearray("Content-Length: {0}\r\n".format(self.file_length), 'utf-8'))
            
            #how to get last modified time https://www.kite.com/python/answers/how-to-get-the-last-modified-time-of-a-file-in-python (Copyright 2022 Kite)
            lastModified = time.strftime("%a, %d %b %Y %H:%M:%S GMT",(time.gmtime(os.path.getmtime(self.updated_path))))
            self.request.send(bytearray("Last-Modified: {0}\r\n".format(lastModified), 'utf-8'))
            self.request.send(bytearray("Location: {0}\r\n\r\n".format(BASEURL + self.path), 'utf-8'))

            
    def bad_request_error(self):
            #HTML format borrowed from https://uofa-cmput404.github.io/cmput404-slides/04-HTTP.html#/20 (Copyright 2014 Abram Hindle, Copyright 2019 Hazel Victoria Campbell and contributors)
            html_400_code = "<html>\r\n"\
                "<head><title>400 BAD REQUEST</title></head>\r\n"\
                "<body bgcolor=\"white\">\r\n"\
                "<center><h1>400</h1></center\r\n>"\
                "<hr><center>BAD REQUEST</center>\r\n"\
                "</body>\r\n"\
                "</html>\r\n"
               
            self.message = "Bad Request"
            self.request.send(bytearray("{0} {1} {2}\r\n".format('HTTP/1.1', self.code, self.message), 'utf-8'))
            self.request.send(bytearray("Server: Gurjog's Server\r\n", 'utf-8'))
            #how to print current GMT time https://www.askpython.com/python/examples/convert-seconds-hours-minutes (Copyright 2022 AskPython )
            datetime_string = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time()))
            self.request.send(bytearray("Date: {0}\r\n".format(datetime_string), 'utf-8'))
            self.request.send(bytearray("Connection: close \r\n", 'utf-8'))
            self.request.send(bytearray("Content-type: text/html;charset=utf-8\r\n", 'utf-8'))
            self.request.send(bytearray("Content-Length: {0}\r\n\r\n".format(len(html_400_code)), 'utf-8'))
            self.request.send(bytearray(html_400_code, 'utf-8'))
        
    def page_not_found_error(self):

            #HTML format borrowed from https://uofa-cmput404.github.io/cmput404-slides/04-HTTP.html#/20 (Copyright 2014 Abram Hindle, Copyright 2019 Hazel Victoria Campbell and contributors)
            html_404_code = "<html>\r\n"\
                "<head><title>404 File Not Found</title></head>\r\n"\
                "<body bgcolor=\"white\">\r\n"\
                "<center><h1>404</h1></center\r\n>"\
                "<hr><center>File Not Found</center>\r\n"\
                "</body>\r\n"\
                "</html>\r\n"
               
            self.message = "File not found"
            self.request.send(bytearray("{0} {1} {2}\r\n".format(self.protocol, self.code, self.message), 'utf-8'))
            self.request.send(bytearray("Server: Gurjog's Server\r\n", 'utf-8'))
            #how to print current GMT time https://www.askpython.com/python/examples/convert-seconds-hours-minutes (Copyright 2022 AskPython )
            datetime_string = time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(time.time()))
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
    
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()

            

