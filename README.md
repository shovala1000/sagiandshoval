# Cloud service

Cloud service for folders and files backup:
Backup and monitor changes within a specific directory including its sub-directories. Allows
users to modify files from different devices while maintaining one synchronized copy of the 
file. Written in Python (supports both Linux and Windows).

# Getting Started
* Clone this repository.
* Run server.py with port number as an argument. The server will listen to this port.
* Run client.py with 4 or 5 arguments in this order:  
  1. Server IP address. 
  2. Server port (as you choose earlier). 
  3. Your folder path (absolute or relative).
  4. Number which is the time you want all your accounts will be synchronized. 
  5. If you have been connected before with this folder put your folder's id.

# Pay attention
* When you will run client.py for the first time you will get as an output the folder's id. 
* Run server.py before you run client.py
* Do not close server.py before you close all the open clients.
