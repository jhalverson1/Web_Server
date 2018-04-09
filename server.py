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
    outputs = []
    topic_dictionary = {}

    def __init__(self):
        print('binding to address: %s port: %s' % self.address)
        self.s.bind(self.address)

        # listen for incoming connections
        self.s.listen(5)

    def run(self):
        print("running...")
        while True:

            # Wait for something to happen
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs)

            # loop through list of readable objects
            for current_read in readable:

                # there is an incoming connection
                if current_read is self.s:
                    client_socket, client_address = current_read.accept()
                    client_socket.setblocking(0)
                    self.inputs.append(client_socket)
                    print("Connections:", len(self.inputs))

                # connection has data for us
                else:
                    data = current_read.recv(4096)

                    # if there is data, send it to all clients in the sender's topic
                    if data:
                        json_data = data.decode('utf-8')  # json.loads(data.decode('utf-8'))

                        # parse json request, raise 400 error for exception
                        try:
                            http_as_list = json_data.split("\n")
                            if len(http_as_list[0].split(" ")) == 3:
                                uri = "static" + (http_as_list[0].split(" "))[1]
                            else:
                                uri = ""
                            content_type = "Content Type:text/html\r\n\r\n"

                            print("\nData:\n")
                            print(json_data)
                            print(http_as_list)
                            print("URI: ", uri)

                            # send contents of file, if file not found, send 404 error
                            try:
                                html_file = open(uri)
                                html_file_content = html_file.read()
                                html_file.close()
                                request_success = "200 OK\r\n"

                            except:
                                print(uri, "not found")
                                html_file_content = "<html><body><p>Error 404: File not found</p></body></html>"
                                request_success = "404 Not Found\r\n"

                        except:
                            print("Bad Request")
                            html_file_content = "<html><body><p>Error 404: File not found</p></body></html>"
                            request_success = "400 Bad Request\r\n"

                        # craft and send header response
                        http_response = "HTTP/1.1 " + request_success + content_type
                        http_response += html_file_content
                        client_socket.send(http_response.encode())

                        # close connection
                        self.inputs.remove(current_read)
                        current_read.close()


server = Server()
server.run()

