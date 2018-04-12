"""
@author Jon Halverson
"""

import socket
import sys
import select
import json

print('...\n...\n...')


class Server:

    ip_address = sys.argv[1]
    port = sys.argv[2]
    address = (ip_address, int(port))
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    inputs = [s]

    def __init__(self):
        print('binding to address: %s port: %s' % self.address)
        self.s.bind(self.address)

        # listen for incoming connections
        self.s.listen(5)

    def run(self):
        print("running...")
        while True:

            # Wait for something to happen
            readable, writable, exceptional = select.select(self.inputs, [], [])

            # loop through list of readable objects
            for current_read in readable:

                # there is an incoming connection
                if current_read is self.s:
                    client_socket, client_address = current_read.accept()
                    client_socket.setblocking(0)
                    self.inputs.append(client_socket)

                # connection has data for us
                else:
                    data = current_read.recv(4096)
                    data = data.decode('utf-8')

                    if data:
                        uri = self.process_http_header(data)
                        content_type = "Content Type:text/html\r\n\r\n"

                        # if uri is not None, else 400 Bad Request
                        if uri is not None:

                            # send contents of file, if file not found, send 404 error
                            try:

                                if uri[-3:] == "jpg":
                                    file = open(uri, 'rb')
                                    file_content = file.read()
                                    file.close()
                                    request_success = "200 OK\r\n"
                                    content_type = "Content Type:image/jpeg\r\n\r\n"

                                elif uri[-3:] == "png":
                                    file = open(uri, 'rb')
                                    file_content = file.read()
                                    file.close()
                                    request_success = "200 OK\r\n"
                                    content_type = "Content Type:image/png\r\n\r\n"

                                else:
                                    file = open(uri)
                                    file_content = file.read()
                                    file.close()
                                    request_success = "200 OK\r\n"
                                    content_type = "Content Type:text/html\r\n\r\n"

                            except:
                                file_content = "<html><body><p>Error 404: File not found</p></body></html>"
                                request_success = "404 Not Found\r\n"

                        else:
                            file_content = "<html><body><p>Error 400: Bad Request</p></body></html>"
                            request_success = "400 Bad Request\r\n"

                        # craft and send header response

                        if uri[-3:] == "jpg":
                            http_response = "HTTP/1.1 " + request_success + content_type
                            client_socket.send(http_response.encode())
                            client_socket.send(file_content)

                        elif uri[-3:] == "png":
                            http_response = "HTTP/1.1 " + request_success + content_type
                            client_socket.send(http_response.encode())
                            client_socket.send(file_content)

                        else:
                            http_response = "HTTP/1.1 " + request_success + content_type + file_content
                            client_socket.send(http_response.encode('utf-8'))

                        self.inputs.remove(current_read)
                        current_read.close()

                    else:
                        # close connection
                        self.inputs.remove(current_read)
                        current_read.close()

    # Find the URI
    def process_http_header(self, data):

        http_as_list = data.split("\r\n")
        header = http_as_list[0].split(" ")
        ending_crlfs = data[-4:]

        if (len(header) == 3) & (header[0] == "GET") & (ending_crlfs == "\r\n\r\n") & (header[2] == "HTTP/1.1"):
            uri = "static" + (http_as_list[0].split(" "))[1]

        else:
            uri = None

        return uri


server = Server()
server.run()

