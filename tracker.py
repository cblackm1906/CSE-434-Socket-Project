#CSE 434 Fall 2024
#Socket Project
#Group 76
#Caleb Blackmon and Gurshan Singh

import socket
import threading

#HEADER = 16
SERVER = input("IP Address: ")
S_PORT = int(input("Port: "))
FORMAT = 'utf-8'
#DISCMSG= "DISCMSG!"

class Tracker:
    def __init__(self):
        self.players = {}
        self.games = {}

    def start(self):
        tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tracker.bind((SERVER,S_PORT))
        print(f"TRACKER RUNNING ON {SERVER, S_PORT}")
        while True:
            conn, addr = tracker.recvfrom(2048)
            thread = threading.Thread(target=self.handle_client, args=(conn,addr,tracker))
            thread.start()

    def register_player(self,request,addr):
        player_name = request[1]
        player_port = request[2]
        peer_port = request[3]

        self.players[player_name] = {
              'address': addr[0], 
              'player port': player_port, 
              'peer port': peer_port, 
              'status': 'free'}
        return f"Player {player_name} registered\nTotal Players: {len(self.players)}\n"

    def query_players(self):
        response = "Players:\n"
        for player_name, details in self.players.items():
            response += (
                f"""{player_name}\n{details['address']}\nPlayer Port: {details['player port']}\nPeer Port: {details['peer port']}\nStatus: {details['status']}\n\n"""
            )
        #response += f"Total Players: {len(self.players)}\n"
        return response

    def query_games(self):
        response = f"Running Games: {len(self.games)}\n"
        return response

    def deregister_player(self, request):
        player_name = request[1]
        del self.players[player_name]
        return f"Player {player_name} deregistered\nTotal Players: {len(self.players)}\n"
        
    def handle_client(self, conn, addr, tracker):
        request = conn.decode(FORMAT).split()
        if request[0] == 'register':
                    response = self.register_player(request,addr)
                    print(response)
        if request[0] == 'query' and request[1] == 'players':
                    response = self.query_players()
                    print(response)
        if request[0] == 'query' and request[1] == 'games':
                    response = self.query_games()
                    print(response)
        if request[0] == 'deregister':
                    response = self.deregister_player(request)
                    print(response)
                    connected = False
        tracker.sendto(response.encode(FORMAT), addr)

tracker = Tracker()
print("SERVER STARTED")
tracker.start()
