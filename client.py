# CS171 Final Project, June 2023
# client.py
# Author: Wenjin Li, An Cao

import socket
import sys
import threading
import json
import os
import time
import random

import BlockChain as BC
import Blog
import MultiPaxos
import Queue

from time import sleep
from os import _exit
from ast import literal_eval


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
        
        self.Paxos = MultiPaxos.Paxos(id=self.name)
        self.Blog = Blog.Blog()

        self.receiceNum = 0
        self.acceptedNum = 0
        self.promise_all_val = []
        self.promises = {}
        
        self.curr_leader = None
        self.virgin_server = True
        self.serverQueue = Queue.Queue()

        #create a dictionary of the connection status of each peer (True/False)
        self.disconnect_flag = {
            'P1': False,
            'P2': False,
            'P3': False,
            'P4': False,
            'P5': False
        }

    def print_ports_dict(self):
        print(f'{self.ports}')

    def start(self):
        #check if this is the first time the server is started by check if the saved file is empty, if not set virgin to false
        # check if {self.name}_info.json is empty
        if os.path.exists(f"{self.name}_log.txt") and os.stat(f"{self.name}_log.txt").st_size != 0:
            self.virgin_server = False
            print(f"{self.name}: I am not a virgin server.")
            
            # delete the old log file
            if os.path.exists(f"{self.name}_BC.json"):
                # os.remove(f"{self.name}_BC.json")
                with open(f"{self.name}_BC.json", 'w'):
                    pass
            if os.path.exists(f"{self.name}_info.json"):
                # os.remove(f"{self.name}_info.json")
                with open(f"{self.name}_info.json", 'w'):
                    pass
            if os.path.exists(f"{self.name}_blog.json"):
                # os.remove(f"{self.name}_blog.json")
                with open(f"{self.name}_blog.json", 'w'):
                    pass
            
        self.server.listen()
        print(f"{self.name}: Server started on port {self.port}")
        self.accept_connections_thread = threading.Thread(target=self.accept_connections).start()

        self.command_thread = threading.Thread(target=self.read_commands).start()
        self.heartbeat_thread = threading.Thread(target=self.send_heartbeat).start()  # 启动heartbeat线程
        
    def checking(self):
        sleep(10)
        self.command_thread = threading.Thread(target=self.ask_depth).start()

    def ask_depth(self):
        if self.virgin_server == False:
            data = {
                "msg_type": "new_depth?",
                "sender": self.name
            }
            depth_msg = json.dumps(data)
            print(f"my peer is peer{self.connections.keys()}")
            self.broadcast_message(depth_msg)
            print(f"{self.name}: I am asking others for the depth of the blockchain.")
            sys.stdout.flush()

    def accept_connections(self):
        while True:
            client, _ = self.server.accept() # address no needed so: _
            threading.Thread(target=self.handle_client, args=(client,)).start()

    def handle_client(self, client):
        client_name = client.recv(1024).decode('utf-8')
        if not client_name:
            return
        self.connections[client_name] = client
        print(f"{self.name}: {client_name} has connected with me.")

        threading.Thread(target=self.receive_messages, args=(client,)).start()
    def read_commands(self):
        global BC_Logs
        while True:

            user_input = input()
            if user_input == '':
                continue

            elif user_input == 'save':
                self.save()

            elif user_input == 'load':
                self.load()

            elif user_input.split()[0] == 'exit':
                print("exiting...")
                self.server.close()
                sys.stdout.flush()
                _exit(0)

            elif user_input.split()[0] == "wait":
                num_sec = int(user_input.split()[1])
                sleep(num_sec)

            elif user_input.split()[0] == "show":
                self.show_command()
                sys.stdout.flush()

            elif user_input.split()[0] == "queue":
                print(self.serverQueue)
                sys.stdout.flush()

            elif user_input.split()[0] == "info":
                print(f"curr_leader is:{self.curr_leader}")
                print(self.Paxos)
                print("This server is connecting with: ", end="")
                for key in self.connections.keys():
                    print(f"{key} ", end="")
                print()
                sys.stdout.flush()

            elif user_input.split()[0] == "failLink" or user_input.split()[0] == "fail":
                dest = user_input.split()[1]
                del self.connections[dest]
                self.disconnect_flag[dest] = True
                print(f"failLink {dest} success")
                sys.stdout.flush()
            
            # fixLink(dest): restore the connection between the issuing process and the dest node
            elif user_input.split()[0] == "fixLink" or user_input.split()[0] == "fix":
                dest = user_input.split()[1]
                self.disconnect_flag[dest] = False
                print(f"fixLink {dest} success")
                # data = {
                #     "msg_type": "check",
                #     "sender": self.name
                # }
                # check_msg = json.dumps(data)
                # self.broadcast_msg_to(id=dest, message=check_msg)
                sys.stdout.flush()

            elif user_input.split()[0] == "BlockChain" or user_input.split()[0]== "BC":
                if len(BC_Logs) == 0:
                    print("[]")
                    sys.stdout.flush()
                    continue
                # print('asked to print the entire blockchain')
                bc_string = ""
                for log in BC_Logs:
                    each_log_str = f"{log.OP}, {log.username}, {log.title}, {log.content}, {log.hash}"
                    bc_string += f"({each_log_str}), "
                print( f'[{bc_string[:-2]}]' )
                sys.stdout.flush()

            elif user_input.split()[0] == 'POST' or user_input.split()[0] == 'COMMENT':
            # message_tokens: POST username title content
            # message_tokens: COMMENT targetUsername targetTitle comments
                authorNtitle = (user_input.split()[1],user_input.split()[2])
                
                if user_input.split()[0] == 'COMMENT':
                    user_input += f" {self.name}"
                if user_input.split()[0] == 'POST' and self.Blog.check_post_exist(authorNtitle):
                    print("this author already has a post with the same title!\n")
                    continue
                if user_input.split()[0] == 'COMMENT' and not self.Blog.check_post_exist(authorNtitle):
                    print(f"Can't not comment. Post not found with:'{authorNtitle[0]}', '{authorNtitle[1]}'\n")
                    continue

                # send PERPARE with BallotNumber
                self.receiceNum = 0
                self.promise_all_val = []
                self.promises = {}
                if self.curr_leader == None: # if curr leader is empty
                    self.Paxos.add_proposal(user_input)
                    message_dict = self.Paxos.prepare().to_dict()
                    message_json = json.dumps(message_dict)
                    self.broadcast_message(message_json) # sending PREPARE
                else: # if curr leader is not empty
                    if self.curr_leader == self.name: # if curr_leader is ourself
                        # add the message to the server queue
                        self.serverQueue.append(user_input)
                    else: # if not ourself
                        msgToLeader = MultiPaxos.Message(msg_type=user_input.split()[0], msg_to_leader=user_input, sender=self.name)
                        msgToLeader_dict = msgToLeader.to_dict()
                        print(f"I am not the leader, sending this msg to leader {self.curr_leader}: {msgToLeader_dict['msg_to_leader']}")
                        msgToLeader_json = json.dumps(msgToLeader_dict)
                        success = self.broadcast_msg_to(self.curr_leader, msgToLeader_json)
                        if not success:
                            print("The leader is down, trying to start the election phase...")
                            self.curr_leader = None
                            self.Paxos.add_proposal(user_input)
                            message_dict = self.Paxos.prepare().to_dict()
                            message_json = json.dumps(message_dict)
                            self.broadcast_message(message_json)
            

            elif user_input.split()[0] == 'view' and user_input.split()[1] == 'all' and user_input.split()[2] == 'posts':
                self.Blog.view_all_posts()
            
            elif user_input.split()[0] == 'view' and user_input.split()[1] == 'posts':
                # view posts USERNAME
                self.Blog.get_posts_by_author(user_input.split()[2])

            elif user_input.split()[0] == 'view' and user_input.split()[1] == 'comments':
                # view comments AUTHOR POST
                authorNtitle = (user_input.split()[2], user_input.split()[3])
                if self.Blog.check_post_exist(authorNtitle):
                    self.Blog.get_post(authorNtitle).get_comment()
            
            else:
                    print(f"{user_input}, wrong input")

    def create_new_post(self,user_input):
        if len(user_input.split()) == 5: blog_str = user_input.split()[:-1]
        else: blog_str = user_input.split()
        hash_val = '0'*64
        if len(BC_Logs) > 0:
            hash_val = BC_Logs[-1].compute_block_hash()
        # blog_str = generate_send_string(sender, message_tokens[1], requested_amt)
        
        new_blog_str = ''
        for i in blog_str: new_blog_str += i
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
        print(f"SUCCESS created a new log in BlockChain: {user_input}")

    def broadcast_message(self, message):
        for peer, connection in list(self.connections.items()):
            try:
                self.send_message(peer, message)
            except BrokenPipeError:
                print(f"{self.name}: Connection to {peer} lost.")
                del self.connections[peer]

    def broadcast_msg_to(self, id, message):
        try:
            self.connections[id].send(message.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Failed to send message to {id}. Reason: {str(e)}")
            return False

    def send_message(self, peer, message):
        message = f"{message}"
        if self.disconnect_flag[peer] == False:
            self.connections[peer].send(message.encode('utf-8'))

    def log_to_txt(self, message):
        with open(f'{self.name}_log.txt','a') as file:
            file.write(f"{message}\n")

    def receive_messages(self, client):
        global BC_Logs
        while True:
            try:
                message_json = client.recv(1024).decode('utf-8')
                if message_json:  # Check if the message is not empty
                    try:
                        message = json.loads(message_json)
                    except json.JSONDecodeError:
                        # print(f'Failed to parse first JSON message: {message_json}')
                        message_json = message_json.replace('}{', '}\n{')
                        message = json.loads(message_json.split('\n', 1)[0])
                        print(type(message))

                    # print(f"\nThe type of received msg: {type(message)}") # it's dict here # TEST USED
                    # print(f"Received in client.py: {message}")
                    self.log_to_txt(f"Received in client.py: {message}")

                    if message["msg_type"] == "ping":
                        data = {
                            "msg_type": "pong",
                            "sender": self.name
                        }
                        pong_message = json.dumps(data)
                        try:
                            self.send_message(message["sender"], pong_message)
                        except Exception:
                            pass
                    
                    elif message["msg_type"] == "pong":
                        # print(f"Pong, from {message['sender']}") # TEST USED
                        pass

                    elif message["msg_type"] == "new_depth?":
                        #find my own local log files that start with self.name and send back to the sender
                        print(f"Received 'new_depth?' from {message['sender']}") # TEST USED
                        if not os.path.exists(f'{self.name}_BC.json'):
                            return
                        
                        with open(f'{self.name}_BC.json', 'r') as file:
                            bc_list = json.load(file) # it's a list of BC.Log objects
                        with open(f'{self.name}_info.json', 'r') as file:
                            server_info = json.load(file) # it's a dict
                        with open(f'{self.name}_blog.json', 'r') as file:
                            blog_dict = json.load(file) # it's a dict
                        
                        # put bc_list, server_info, blog_dict into a dict and send back to the sender
                        data = {
                            "msg_type": "new_depth!",
                            "sender": self.name,
                            "bc_list": bc_list,
                            "server_info": server_info,
                            "blog_dict": blog_dict
                        }
                        new_depth_message = json.dumps(data)
                        sleep(int(self.name[1:]))
                        self.send_message(message["sender"], new_depth_message)

                    elif message["msg_type"] == "new_depth!":
                        # recovery the received bc_list, server_info, blog_dict
                        print(f"Received 'new_depth!' from {message['sender']}") # TEST USED
                        # if the depth of received BC is deeper than self, update self's all files
                        if int(message["server_info"]["depth"]) > self.Paxos.depth:
                            # load the received bc_list
                            bc_list= message["bc_list"]
                            BC_Logs = [BC.Log(**log_dict) for log_dict in bc_list]

                            # load the received server_info
                            self.curr_leader = message["server_info"]['curr_leader']
                            # Reconstructing the Paxos instance with saved state
                            self.Paxos.ballot_num = message["server_info"]['ballot_num']
                            self.Paxos.ballot_num_id = message["server_info"]['ballot_num_id']
                            self.Paxos.depth = message["server_info"]['depth']
                            self.Paxos.accepted_ballot_num = message["server_info"]['accepted_ballot_num']
                            self.Paxos.accepted_ballot_num_id = message["server_info"]['accepted_ballot_num_id']
                            self.Paxos.accepted_value = message["server_info"]['accepted_value']
                            self.Paxos.proposal = message["server_info"]['proposal']
                            
                            # load the received blog_dict
                            blog_dict = message["blog_dict"]
                            blog_list = {literal_eval(key): Blog.Post.from_dict(post) for key, post in blog_dict.items()}
                            self.Blog.blog_list = blog_list

                    elif message["msg_type"] == "check":
                        data = {
                            "msg_type": "new_depth?",
                            "sender": self.name
                        }
                        depth_msg = json.dumps(data)
                        print(f"my peer is peer{self.connections.keys()}")
                        self.broadcast_message(depth_msg)
                        print(f"{self.name}: I am asking others for the depth of the blockchain.")
                        sys.stdout.flush()

                    elif message["msg_type"] == "POST" or message["msg_type"] == "COMMENT":
                        if self.curr_leader == self.name:
                        # know my self is leader, and others know myself is leader
                            self.receiceNum = 0
                            self.promise_all_val = []
                            self.promises = {}
                            self.serverQueue.append(message["msg_to_leader"])
                        else:
                        #if leader is not self, redirect the message to the known leader again
                            msgToLeader = MultiPaxos.Message(msg_type=message["msg_type"], msg_to_leader=message["msg_to_leader"], sender=self.name)
                            self.broadcast_msg_to(self.curr_leader, msgToLeader)
                            
                    elif message["msg_type"] == "PREPARE": #  non-leader handling
                        # print this msg's content, and return a PROMISE msg to be pre_PROMISE_msg
                        pre_PROMISE_msg = self.Paxos.receive_prepare(message)
                        # print(f"Received in client.py: {pre_PROMISE_msg.id}")
                        if pre_PROMISE_msg is not None: # if not rejected
                            pre_PROMISE_dict = pre_PROMISE_msg.to_dict()
                            message_json = json.dumps(pre_PROMISE_dict)
                            # send PROMISE to leader
                            self.broadcast_msg_to(id=pre_PROMISE_dict['ballot_num_id'], message=message_json)
                            # set the sender to curr_leader
                            self.curr_leader =  message['sender']

                    elif message["msg_type"] == "PROMISE": # Phase two: handling all promise msg
                        print(f"Received from {message['sender']}: {message['msg_type']} <{message['ballot_num']},{message['ballot_num_id']}> <{message['accepted_num']},{message['accepted_num_id']}> {message['accepted_val']} depth={message['depth']}")
                        self.receiceNum += 1
                        self.promise_all_val.append(message['accepted_val']) # used to check if all received msg is all None
                        self.promises[message['sender']] = message
                        if self.receiceNum >= (len(self.peers)-1) / 2:  # More than half peers/majority responded
                            print("Received majority promise and enter critical situatuion")
                            self.receiceNum = -999
                            
                            # set myself to be a leader:
                            self.curr_leader = self.name
                            
                            # print(f"before chceking if all None, receiceNum={self.receiceNum}")
                            if all(x is None for x in self.promise_all_val):
                                # print("im here1")
                                # myVal = initial_value
                                self.Paxos.update_my_accepted_value()
                                # send ACCEPT to all 
                                message_dict = self.Paxos.received_majority_promise().to_dict()
                                message_json = json.dumps(message_dict)
                                self.broadcast_message(message_json)
                                self.promise_all_val = []
                                self.promises = {}
                                
                            else: # check who's accepted value is the largest one
                                print("goes into the else case")
                                # find the largest accepted value's Massage
                                highest_b_message = max(self.promises.values(), key=lambda m: m['accepted_num'])
                                # print(highest_b_message)
                                self.Paxos.update_my_accepted_value(highest_b_message['accepted_val'])
                                
                                # send ACCEPT to all 
                                message_dict = self.Paxos.received_majority_promise().to_dict()
                                message_json = json.dumps(message_dict)
                                self.broadcast_message(message_json)
                                self.promise_all_val = []
                                self.promises = {}
                        else:
                            # print(f"waiting more PROMISE")
                            pass

                    elif message["msg_type"] == "ACCEPT": # Phase two: non-leader handling ACCEPT msg
                        # ACCEPT <1,P1> 'POST username title content'
                        msg = self.Paxos.receive_accept(message)
                        if msg is not None:
                            msg_in_dict= msg.to_dict()
                            message_json = json.dumps(msg_in_dict)
                            # send ACCEPTED to leader
                            self.broadcast_msg_to(id=msg.accepted_num_id, message=message_json)
                        else:
                            print(f"I have a highter ballot num than {message['sender']}")

                    elif message["msg_type"] == "ACCEPTED": # leader phase
                        # ACCEPTED <1,P1> 'POST username title content' depth=x
                        print(f"Received from {message['sender']}: {message['msg_type']} <{message['accepted_num']},{message['accepted_num_id']}> {message['accepted_val']} depth={message['depth']}")
                        # print(f"\t\ttype: {type(message['depth'])}")
                        
                        if str(message['depth']) in ACCEPTED_counter_dict:
                            ACCEPTED_counter_dict[str(message['depth'])] += 1
                        else:
                            ACCEPTED_counter_dict[str(message['depth'])] = 1

                        print(f"current accepted num counter: {ACCEPTED_counter_dict[str(message['depth'])]}")
                        # print(len(self.peers))
                        sleep(2)
                        if ACCEPTED_counter_dict[str(message['depth'])] >= (len(self.peers)-1) / 2:  # More than half peers/majority responded
                            
                            ACCEPTED_counter_dict[str(message['depth'])] = -999
                            
                            print("enter majority decide")
                            self.Paxos.depth_increment() # depth += 1
                            
                            # send DECIDE to all
                            message_dict = self.Paxos.received_majority_accepted(message['accepted_val']).to_dict()
                            message_json = json.dumps(message_dict)
                            self.broadcast_message(message_json)

                            # create a new post to leader's block chain
                            self.create_new_post(message['accepted_val'])

                            if message['accepted_val'].split()[0] == 'POST':
                                self.Blog.makeNewPost(Blog.Post(message['accepted_val'].split()[1], message['accepted_val'].split()[2], message['accepted_val'].split()[3]))
                                print(f"SUCCESS created a new POST in Blog: {message['accepted_val']}\n")

                            if message['accepted_val'].split()[0] == 'COMMENT':
                                authorNtitle = (message['accepted_val'].split()[1], message['accepted_val'].split()[2])
                                comment = message['accepted_val'].split()[3]
                                if self.Blog.check_post_exist(authorNtitle):
                                    if not self.Blog.get_post(authorNtitle).check_comment_exist(message['accepted_val'].split()[1],message['accepted_val'].split()[3]):
                                        self.Blog.get_post(authorNtitle).add_comment(follower=message['accepted_val'].split()[4], new_content=comment)
                                    else:
                                        print(f"Error! This comment already existed:\n\t{message['accepted_val'].split()[4]}: {comment}\n")
                            # clear the cache
                            self.Paxos.clear()
                            self.save()


                    elif message["msg_type"] == "DECIDE":
                        # DECIDE <1,P1> 'POST username title content'
                        print(f"Received from {message['sender']}: {message['msg_type']} <{message['ballot_num']},{message['ballot_num_id']}> {message['accepted_val']} depth={message['depth']}")
                    
                        # create a new post to non-leader's block chain
                        self.create_new_post(message['accepted_val'])

                        if message['accepted_val'].split()[0] == 'POST':    
                            self.Blog.makeNewPost(Blog.Post(message['accepted_val'].split()[1], message['accepted_val'].split()[2], message['accepted_val'].split()[3]))
                            print(f"SUCCESS created a new POST in Blog: {message['accepted_val']}\n")

                        elif message['accepted_val'].split()[0] == 'COMMENT':
                            authorNtitle = (message['accepted_val'].split()[1], message['accepted_val'].split()[2])
                            comment = message['accepted_val'].split()[3]
                            if self.Blog.check_post_exist(authorNtitle):
                                if not self.Blog.get_post(authorNtitle).check_comment_exist(message['accepted_val'].split()[1],message['accepted_val'].split()[3]):
                                        self.Blog.get_post(authorNtitle).add_comment(follower=message['accepted_val'].split()[4], new_content=comment)
                                else:
                                    print(f"Error! This comment already existed:\n\t{message['accepted_val'].split()[4]}: {comment}\n")
                        
                        self.curr_leader = message["sender"]
                        self.Paxos.depth += 1
                        # clear the cache
                        self.Paxos.clear()
                        self.save()
                    
                # else:
                    # print("receive_messages() receive nothings")
        
            except ConnectionResetError:
                # print("ConnectionResetError")
                sys.stdout.flush()
                break
            
    def save(self):
         # save the BC
        bc_list = [log.__dict__ for log in BC_Logs]
        with open(f'{self.name}_BC.json','w') as file:
            json.dump(bc_list, file)
        print("SAVED BC")
        # save the info
        server_info = {
            'curr_leader': self.curr_leader,
            'id': self.Paxos.id,
            'ballot_num': self.Paxos.ballot_num,
            'ballot_num_id': self.Paxos.ballot_num_id,
            'depth': self.Paxos.depth,
            'accepted_ballot_num': self.Paxos.accepted_ballot_num,
            'accepted_ballot_num_id': self.Paxos.accepted_ballot_num_id,
            'accepted_value': self.Paxos.accepted_value,
            'proposal': self.Paxos.proposal
        }
        with open(f'{self.name}_info.json', 'w') as file:
            json.dump(server_info, file)
        print("SAVED info")
        # save the Blog class
        with open(f'{self.name}_blog.json', 'w') as file:
            blog_dict = {str(key): post.to_dict() for key, post in self.Blog.blog_list.items()}
            json.dump(blog_dict, file)
        print("SAVED blog")

    def load(self):
        # load the BC
        with open(f'{self.name}_BC.json','r') as file:
            bc_list = json.load(file)
        BC_Logs = [BC.Log(**log_dict) for log_dict in bc_list]
        print("LOADED BC")

        # load the info
        with open(f'{self.name}_info.json', 'r') as file:
            server_info = json.load(file)
        
        # if self.name == server_info['curr_leader']:
            # self.curr_leader = None
        self.curr_leader = server_info['curr_leader']
        # Reconstructing the Paxos instance with saved state
        self.Paxos.id = server_info['id']
        self.Paxos.ballot_num = server_info['ballot_num']
        self.Paxos.ballot_num_id = server_info['ballot_num_id']
        self.Paxos.depth = server_info['depth']
        self.Paxos.accepted_ballot_num = server_info['accepted_ballot_num']
        self.Paxos.accepted_ballot_num_id = server_info['accepted_ballot_num_id']
        self.Paxos.accepted_value = server_info['accepted_value']
        self.Paxos.proposal = server_info['proposal']
        print("LOADED info")

        # load the Blog class
        with open(f'{self.name}_blog.json', 'r') as file:
            blog_dict = json.load(file)
        blog_list = {literal_eval(key): Blog.Post.from_dict(post) for key, post in blog_dict.items()}
        self.Blog.blog_list = blog_list
        print("LOADED blog")


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
                #check if the disconnect flag is true, if true, then skip this peer
                if self.disconnect_flag[peer] == True:
                    continue
                self.connect_to_peer(peer)
            sleep(2)
    #         # print("trying to reconnecting to other peer")

    def send_heartbeat(self):
        while True:
            for peer, connection in list(self.connections.items()):
                try:
                    data = {
                        "msg_type": "ping",
                        "sender": self.name
                    }
                    message = json.dumps(data)
                    self.send_message(peer, message)
                except BrokenPipeError:
                    print(f"{self.name}: Connection to {peer} lost.")
                    del self.connections[peer]
                    if peer == self.curr_leader:
                        print(f"The leader {peer} is down, next CLI will start the election phase now...")
                        self.curr_leader = None
                        self.Paxos.clear()
            sleep(8) # send heartbeat each 15 second

    def check_peers(self):
        while True:
            for peer in list(self.connections.keys()):
                try:
                    self.connections[peer].send("CHECK".encode('utf-8'))  # send a check message
                    sleep(2)  # wait for a response
                    self.connections[peer].recv(1024).decode('utf-8')  # try to receive a response
                except Exception as e:  # failed to receive a response
                    print(f"Lost connection to {peer}. Reason: {str(e)}")
                    if peer == self.curr_leader:
                        print(f"The leader {peer} is down, trying to start the election phase now...")
                        self.curr_leader = None
                    del self.connections[peer]  # remove the peer from the connections list
            sleep(10)  # check every 10 seconds

    def show_command(self):
        print("BlockChain or BC")
        print("failLink")
        print("fixLink")
        print("POST username title content")
        print("COMMENT username title content")
        print("view all posts")
        print("view posts USERNAME")
        print("view comments AUTHOR POST")
        print("info")
        print("wait x")
        print("exit")
        print("")

    #handle the request in the queue by pick the first request in the queue and pop if after handling it
    def handle_queue(self):
        while True:
            #check if self is leader, if not, flush the queue
            if self.curr_leader != self.name:
                self.serverQueue = []
                sleep(0.1)
                continue
            else:
                if len(self.serverQueue) > 0:
                    request = self.serverQueue.pop(0)
                    print(f"about to start handle the request: '{request}'")
                    self.handle_request(request)
                sleep(3)

    def handle_request(self, request):
        # send to accept msg all
        message_dict = self.Paxos.leader_send_accept(request).to_dict()
        message_json = json.dumps(message_dict)
        self.broadcast_message(message_json)
        
################      global      ################
BC_Logs = []
ACCEPTED_counter_dict = {}

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
    
    # create a new thread to handle the operations stored in the queue
    threading.Thread(target=server.handle_queue, args=()).start()

    threading.Thread(target=server.connect_to_peers, args=()).start()

    print(f"{server.name}: I have finished setting up the server!")
    server.checking()
