import socket
import threading

    
#HEADER = 16
SERVER = input("IP Address: ")
FORMAT = 'utf-8'
#DISCMSG= "DISCMSG!"

player_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

player_name = input("Player Name: ")
tracker_addr = input("Tracker Address: ")
tracker_port = int(input("Tracker Port: "))
player_port = int(input("Player Port: "))
peer_port = int(input("Peer Port: "))

class Player:

    def __init__(self,player_name,tracker_addr,tracker_port, player_port, peer_port):
        self.player_name = player_name
        self.tracker_addr = tracker_addr
        self.tracker_port = tracker_port
        self.player_port = player_port
        self.peer_port = peer_port

    def register(self):
        message = f"register {self.player_name} {self.player_port} {self.peer_port}"
        self.send_msg(message)

    def query_players(self):
        message = "query players"
        self.send_msg(message)

    def query_games(self):
        message = "query games"
        self.send_msg(message)

    def deregister(self):
        message = f"deregister {self.player_name}"
        self.send_msg(message)

    def send_msg(self, message):
        player_socket.sendto(message.encode(), (self.tracker_addr, self.tracker_port))
        conn, _ = player_socket.recvfrom(2048)
        print(f"{conn.decode(FORMAT)}")

player = Player(player_name, tracker_addr, tracker_port, player_port, peer_port)

connected = True
while connected:
        ms = input("\nSelect Your Choice!\n1. Register\n2. Query Players\n3. Query Games\n4. Deregister\n: ")
        if ms == "0":
            exit()
        elif ms == "1":
            #name = input("Name: ")
            player.register()
        elif ms == "2":
            player.query_players()
        elif ms == "3":
            player.query_games()
        elif ms == "4":
            player.deregister()
            connected = False
        else:
            print("Invalid Selection\n")
