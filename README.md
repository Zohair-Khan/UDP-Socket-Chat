# UDP Socket Chat Program

This is a UDP socket based chat server and client program written in Python. The server allows multiple clients to connect simultaneously and communicate with each other through public and direct messages.

## Included Files

- **chatclient.py**: The client-side program used to connect to the chat server.
    - Handles "message type" arguments from users, sends "command" messages to the server, and receives "data" messages from the server.
    - Sends client login, DM, PM, and exit commands to the server.
    - Implements multithreading to simultaneously receive messages and take commands in the terminal.

- **chatserver.py**: The server-side program responsible for managing client connections and facilitating communication between clients.
    - Handles "command" messages from clients, and sends "data" messages to clients.
    - Handles Login, DM, and PM commands from clients.
    - Pickles usernames and passwords when the server is closed.
    - Implements multithreading to simultaneously receive messages, broadcast messages, and take commands in the terminal.

- **logindata.pkl**: A file containing saved login information, allowing users to log in with their username and password.
    - Loaded to chat server as a Python dictionary matching usernames to passwords.

## How to Run the Chat Server

1. **Place logindata.pkl**: Ensure that the provided logindata.pkl file is in the same directory as your server code (chatserver.py).
   
2. **Run the Server**: Execute the webserver.py file. The program requires command-line arguments that specify the chat server's IP address/hostname and port. Use the following command format: `python3 chatserver.py <server_host> <server_port>`. For example:
    ```
    python3 chatserver.py localhost 9999
    ```
3. **Manage Server**: You can perform additional actions in the server terminal:
- To clear all saved logins, type `CLEAR`.
- To close the server and save all changes to logins, type `EXIT`.

## How to Use the Chat Client

1. **Run the Client**: Execute the webclient.py file. The program requires command-line arguments that specify the chat server's IP address/hostname, port, and your desired username. Use the following command format: `python3 chatclient.py <server_host> <server_port> <username>`. For example:
    ```
    python3 chatclient.py localhost 9999 johndoe
    ```

2. **Login**: Enter your password when prompted. If it's your first time logging in, your username and password will be saved for future use. If you enter an incorrect password, the client will terminate, and you'll need to run webclient.py again.

3. **Send Messages**: Enter one of three commands:
- `PM`: Public Message. Enter a message you want to send to all active users. You will receive a copy of your message if it's successfully broadcasted.
- `DM`: Direct Message. Enter the username of the user you want to send a direct message to, followed by the message. You will receive a copy of your message if it's successfully delivered, and an error message if not.
- `EX`: Exit Command. Terminate the chat client when you're finished using it.