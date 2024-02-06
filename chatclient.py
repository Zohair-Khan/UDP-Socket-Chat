"""
Zohair Khan
ICS 460

Client side of an "online chat room" application using UDP.          
    - Handles "message type" arguments from users, sends "command" messages to server, and receives "data" messages from server.
    - Sends client login, DM, PM, and exit commands to server
    - Implements multithreading to simultaneously receive messages and take commands in terminal
"""
from socket import *
import threading
import random
import time
import sys

SERVERHOST = sys.argv[1] #'localhost'
SERVERPORT = int(sys.argv[2]) #9999
SERVERHOSTPORT = (SERVERHOST,SERVERPORT)

# Bind client to server at random port between 8000-9000
client = socket(AF_INET, SOCK_DGRAM)
client.bind((SERVERHOST, random.randint(8000,9000)))

# LOGINSUCCESSFUL = False

LOGINMESSAGE = "LN" # Login command
QUITMESSAGE = "EX" # Exit command
PUBLICMESSAGE = "PM" # Public message command
DIRECTMESSAGE = "DM" # Direct message command
ONLINEUSERS = "UR" # Online users command

stop_receive = False # Helper boolean used to stop receive() thread

# Continuously receive and print messages from server
def receive():
    while not stop_receive:
        try:
            message, _ = client.recvfrom(1024)
            print(message.decode())         
        except:
            pass

# Login function
# def login(name, LOGINSUCCESSFUL):
def login(name):
    password = input("Password: ")
    client.sendto(f"{LOGINMESSAGE}:{name}#{password}".encode(), SERVERHOSTPORT) # Sends login message to server
    loginmessage, _ = client.recvfrom(1024) # If login fails, server sends message "LOGINFAILED"
    if(loginmessage.decode() == "LOGINFAILED"):
        print("Login failed!")
        return False
    else:
        return True



def main():
    name = sys.argv[3] #input("Username: ")
    
    if login(name):
        
        # receive() thread
        t = threading.Thread(target=receive, daemon = True) 
        t.start()

        while True:
            messagetype = input("PM (Public Message), DM (Direct Message), EX (Exit):\n")
            
            if messagetype == PUBLICMESSAGE: # PM command
                message = input("PM: ") # PM contents
                client.sendto(f"{PUBLICMESSAGE}#{name}:{message}".encode(), SERVERHOSTPORT)
                time.sleep(0.3)
            elif messagetype == QUITMESSAGE: # Exit command
                client.sendto(f"{QUITMESSAGE}#{name}".encode(), SERVERHOSTPORT) # Send exit comment to server
                break
            elif messagetype == DIRECTMESSAGE: # DM command
                client.sendto(f"{ONLINEUSERS}".encode(), SERVERHOSTPORT) # Request list of online users from server, server will respond with list
                time.sleep(0.3)
                targetuser = input("Send to: ") # Select user to DM
                message = input(f"DM@{targetuser}: ") # DM contents
                client.sendto(f"{DIRECTMESSAGE}#{name}@{targetuser}:{message}".encode(), SERVERHOSTPORT) # Send DM to server
                time.sleep(0.3)
            else: # Invalid command
                print(f"Invalid Command: {messagetype}")

    client.close() # Close client socket
    exit()
        
main()