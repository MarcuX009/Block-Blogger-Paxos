# CS171 Final Project, June 2023
# client.py
# Author: Wenjin Li

import socket
import sys
import threading
import time

import BlockChain as BC
import Blog

from time import sleep
from os import _exit


class Server:
    def __init__(self, host='localhost', port=9000):
        self.host = host
        self.port = port
        # linstening socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # SO_REUSEADDR allowing it to bind to the same address \
        #   even if it's still in use by a previous connection.
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.host, self.port))
        self.connections = {}
        self.peers = ['P1', 'P2', 'P3', 'P4', 'P5']
        self.ports = {peer: 9000 + i for i, peer in enumerate(self.peers)}
        self.name = [peer for peer, port in self.ports.items() if port == self.port][0]
    
    def print_ports_dict(self):
        print(f'{self.ports}')
    def start(self):
        self.server.listen()
        print(f"{self.name}: Server started on port {self.port}")
        self.accept_connections_thread = threading.Thread(target=self.accept_connections).start()

        self.command_thread = threading.Thread(target=self.read_commands).start()

    def accept_connections(self):
        while True:
            client, _ = self.server.accept() # address no needed so: _
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        client_name = client.recv(1024).decode('utf-8')
        if not client_name:
            return
        self.connections[client_name] = client
        print(f"{self.name}: Connection established with {client_name}")

        threading.Thread(target=self.receive_messages, args=(client,)).start()

    def read_commands(self):
        while True:
            # message = input()
            # self.broadcast_message(message)
            user_input = input()
            if user_input.split()[0] == 'exit':
                print("exiting...")
                break
            elif user_input.split()[0] == 'BlockChain' or user_input.split()[0] == 'BC':
                if len(BC_Logs) == 0:
                    print("[]")
                    sys.stdout.flush()
                    continue
                # print('asked to print the entire blockchain')
                bc_string = ""
                for log in BC_Logs:
                    each_log_str = f"{log._OP}, {log._username}, {log._title}, {log._content}, {log.hash}"
                    bc_string += f"({each_log_str}), "
                print( f'[{bc_string[:-2]}]' )
                sys.stdout.flush()
            elif user_input.split()[0] == 'POST' or user_input.split()[0] == 'P':
            # message_tokens: POST username title content
                if BC.check_if_post_exist(user_input.split()[1],user_input.split()[2]):
                    print("this author already has a post with the same title!")
                else:
                    self.create_new_post(user_input)
                    self.broadcast_message(user_input)
            else:
                    print(f"{user_input}, worong input")

    def create_new_post(self,user_input):
        hash_val = '0'*64
        if len(BC_Logs) > 0:
            hash_val = BC_Logs[-1].compute_block_hash()
        # blog_str = generate_send_string(sender, message_tokens[1], requested_amt)
        blog_str = user_input.split()
        new_blog_str = ''
        for i in blog_str:
            new_blog_str += i
        right_nonce = BC.compute_nonce(f'{hash_val}{new_blog_str}')
        new_log = BC.Log(
            hash = hash_val,
            OP = user_input.split()[0],
            username = user_input.split()[1],
            title = user_input.split()[2],
            content = user_input.split()[3],
            nonce = right_nonce,
        )
        BC_Logs.append(new_log)
        print(f"SUCCESS created a new post: {user_input}")



    def broadcast_message(self, message):
        for peer, connection in self.connections.items():
            try:
                self.send_message(peer, message)
            except BrokenPipeError:
                print(f"{self.name}: Connection to {peer} lost.")
                del self.connections[peer]

    def send_message(self, peer, message):
        message = f"{self.name}: {message}"
        self.connections[peer].send(message.encode('utf-8'))

    def receive_messages(self, client):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message:
                    print(f"Received: {message}")
                    if message.split()[1] == 'POST' or message.split()[1] == 'P':
                        message = message[4:] # cut the "Px: " and save the rest of the msg
                        print(f"new meg: {message}")
                    # message_tokens: POST username title content
                        if BC.check_if_post_exist(message.split()[1],message.split()[2]):
                            print("this author already has a post with the same title!")
                        else:
                            self.create_new_post(message)

            except ConnectionResetError:
                print("ConnectionResetError")
                sys.stdout.flush()
                break

    def connect_to_peer(self, peer):
        if peer != self.name and peer not in self.connections and self.ports[peer] > self.port:
            try:
                client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client.connect((self.host, self.ports[peer]))
                client.send(self.name.encode('utf-8'))
                self.connections[peer] = client
                print(f"{self.name}: Connected to {peer}")

                threading.Thread(target=self.receive_messages, args=(client,)).start()
            except ConnectionRefusedError:
                pass

    def connect_to_peers(self):
        while True:
            for peer in self.peers:
                self.connect_to_peer(peer)
            sleep(2)
            # print("trying to reconnecting to other peer")

BC_Logs = []

################     __main__     ################
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Need to provide an ID of the client process')
        _exit(0)
    
    # clients sleep for 1 second as soon as they are up.
    sleep(1)
    client_name = sys.argv[1]
    port = 9000 + ['P1', 'P2', 'P3', 'P4', 'P5'].index(client_name)
    server = Server(port=port)
    server.start()
    threading.Thread(target=server.connect_to_peers, args=()).start()

    # server.print_ports_dict()
    print("I have finished setting up the server!")
