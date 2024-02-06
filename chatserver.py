"""
Zohair Khan
ICS 460

Server side of an "online chat room" application using UDP.          
    - Handles "command" messages from clients, and sends "data" messages to clients.
    - Handles Login, DM, and PM commands from clients 
    - Pickles usernames and passwords when server is closed
    - Implements multithreading to simultaneously receive messages, broadcast messages, and take commands in terminal
"""
from socket import *
import threading
import queue
import pickle
import sys

messagequeue = queue.Queue() # Queue that stores incoming messages

usernamepassword = {} # Dictionary of usernames and passwords; pickled to store logins 

# Read login information from pickle
with open('logindata.pkl', 'rb') as fp:
    usernamepassword = pickle.load(fp)
    print("Logins loaded.")

usernameaddress = {} # Dictionary that takes a username and returns a corresponding client address
addressusername = {} # Dictionary that takes a client address and returns a corresponding username
clients = [] # List of active client addresses

#UDP Socket
server = socket(AF_INET, SOCK_DGRAM)
HOST = sys.argv[1] #'localhost'
PORT = int(sys.argv[2]) # 9999
HOSTPORT = (HOST,PORT)
server.bind(HOSTPORT)

LOGINMESSAGE = "LN" # Login command
QUITMESSAGE = "EX" # Exit command
PUBLICMESSAGE = "PM" # Public message command
DIRECTMESSAGE = "DM" # Direct message command
ONLINEUSERS = "UR" # Helper command for DMs

# Helper booleans to stop receive() and broadcast() threads
stop_receive = False 
stop_broadcast = False


def receive():
    while not stop_receive:
        try:
            message, address = server.recvfrom(1024)
            messagequeue.put((message, address))
        except:
            pass

def broadcast():
    while not stop_broadcast:
        while not messagequeue.empty(): # While message queue is not empty, handle messages in queue
            message, address = messagequeue.get()
            print(message.decode())
            if address not in clients: # Add message sender address to list of clients if new
                clients.append(address)
            for client in clients: #Loop through clients for each message
                try:   
                    # Login message handler                
                    if message.decode().startswith(LOGINMESSAGE): # Read username and password from signup tag
                        # Parse username and password from message
                        name = message.decode()[message.decode().index(":")+1:message.decode().index("#")]
                        password = message.decode()[message.decode().index("#")+1:]
                        if name not in usernamepassword: # If username doesn't exist, create new user and log them in, saving the new login
                            usernamepassword[name] = password
                            # Assign client to username (and vice versa)
                            usernameaddress[name] = client
                            addressusername[client] = name
                            # Join message
                            print(f"NEW USER: {name}")
                            server.sendto(f"{name} joined!".encode(), client)
                        elif name in usernamepassword: # If username does exist, compare password to save password
                            if usernamepassword[name] == password: # Password matches, log user in
                                # Assign client to username (and vice versa)
                                usernameaddress[name] = client
                                addressusername[client] = name
                                # Join message
                                print(f"LOGIN SUCCESSFUL: {name}")
                                server.sendto(f"{name} joined!".encode(), client)
                            elif usernamepassword[name] != password: # Password doesn't match, send error message and disconnect user
                                server.sendto("LOGINFAILED".encode(), address)
                                print(f"LOGIN FAILED: {name}")
                                clients.remove(address) # remove failed login address from list of clients
                                break
                    
                    # QUIT message handler: "EX#{name}"
                    elif message.decode().startswith(QUITMESSAGE):
                        name = message.decode()[message.decode().index("#")+1:] # Parse username from message
                        # print(f"QUIT: {name}:{usernameaddress[name]}")
                        # Remove client that corresponds to username from records
                        clients.remove(usernameaddress[name]) 
                        del addressusername[usernameaddress[name]]
                        del usernameaddress[name]
                        break
                    
                    # PUBLIC message handler: "PM#{name}:{message}"
                    elif message.decode().startswith(PUBLICMESSAGE):
                        # Parse username and PM contents from message
                        name = message.decode()[message.decode().index("#")+1:message.decode().index(":")]
                        pub_message = message.decode()[message.decode().index(":")+1:]
                        # print(f"{PUBLICMESSAGE} {name}@all: {pub_message}")
                        # Send PM to all users
                        server.sendto(f"{name}@all: {pub_message}".encode(), client)
                        

                    # ONLINEUSERS message handler: "UR"
                    elif message.decode().startswith(ONLINEUSERS):                      
                        online_users = [username for username in usernameaddress]
                        server.sendto(f"{online_users}".encode(), address) # Send list of online users to client 
                        break

                    # DIRECT message handler: "DM#{name}@{targetuser}:{message}"
                    elif message.decode().startswith(DIRECTMESSAGE):
                        # Parse sender username, target username, and DM contents from message
                        sender = message.decode()[message.decode().index("#")+1:message.decode().index("@")]
                        target = message.decode()[message.decode().index("@")+1:message.decode().index(":")]
                        dir_message = message.decode()[message.decode().index(":")+1:]
                        
                        # If target address exists, send DM to target and send a copy of DM to sender for confirmation
                        if usernameaddress.get(target) != None:
                            try:
                                # Send DM
                                # print(f"{DIRECTMESSAGE} {sender}@{target}: {dir_message}")
                                server.sendto(f"{sender}@{target}: {dir_message}".encode(), usernameaddress.get(target))
                                server.sendto(f"{sender}@{target}: {dir_message}".encode(), address)
                            except:
                                # Send Error message if DM fails to send
                                print(f"Failed to send message from {sender} to {target}")
                                server.sendto(f"Failed to send message from {sender} to {target}!".encode(), address)
                        else:
                            # Send Error message if DM fails to send
                            print(f"Failed to send message from {sender} to {target}")
                            server.sendto(f"Failed to send message from {sender} to {target}!".encode(), address)

                        break

                except: #remove client exceptions from records
                    del usernameaddress[addressusername[client]]
                    del addressusername[client]
                    clients.remove(client)
                    print(f"CLIENT EXCEPTION: {client} REMOVED")

def main():
    # receive() and broadcast() threads
    t1 = threading.Thread(target=receive, daemon = True)
    t2 = threading.Thread(target=broadcast, daemon = True)
    t1.start()
    t2.start()
    
    while True:
        command = input("\n")
        if command == "CLEAR": # Remove all stored usernames and passwords
            usernamepassword = {}
            print("Saved logins cleared.")
        elif command == "EXIT": # Shutdown server
            stop_receive = True
            stop_broadcast = True
            # "Pickle" login information
            with open('logindata.pkl', 'wb') as fp:
                pickle.dump(usernamepassword, fp)
                print("Logins saved successfully to 'logindata.pkl'")
            break

    server.close() # Close server socket
    exit()

main()
