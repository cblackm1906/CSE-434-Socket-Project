# CSE 434 
# Fall 2024
# Socket Project
# Group 76
# Caleb Blackmon and Gursharan Singh
# Reference video used for Socket Programming in Python https://www.youtube.com/watch?v=3QiPPX-KeSc

import socket
import threading
import random

# This prompts the user to save the IP address of the tracker
SERVER = input("IP Address: ")
# This prompts the user to save the port of the tracker
S_PORT = int(input("Port: "))
# Used for uniform decoding of messages to utf-8
FORMAT = 'utf-8'

# The class Tracker is used to create an instance of the tracker. Right now we don't know if we need multiple instances, but just
# in case, we have the ability
class Tracker:
    # Initializes the tracker with an empty players list and an empty games list
    def __init__(self):
        self.players = {}
        self.games = {}

        # This creates a way to manage multiple games at once by assigning an ID
        self.game_id = 0

    # The start function allows the tracker to recieve messages from players. It binds the address and port entered at the 
    # beginning of the program.
    def start(self):
        # Creates a socket instance using IPv4 and UDP structure
        tracker = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tracker.bind((SERVER,S_PORT))
        print(f"TRACKER RUNNING ON {SERVER, S_PORT}")
        # While true makes the server run infinitely, will implement graceful exit later on
        while True:
            conn, addr = tracker.recvfrom(2048)
            # This creates a thread instance to allow for multiple threads to run in parallel
            # The new connection is then directed to the handle_client function
            thread = threading.Thread(target=self.handle_client, args=(conn,addr,tracker))
            thread.start()

    # This function registers a player with the given parameters from the player message requesting to register.
    # The players address, name, port, and peer port are used to create a new player and add them to the players list.
    def register_player(self,request,addr):
        player_name = request[1]
        player_port = request[2]
        peer_port = request[3]

        self.players[player_name] = {
              'address': addr[0], 
              'player port': player_port, 
              'peer port': peer_port, 
              'status': 'free',
              'game ID' : 'None'}
        # This returns the message that the player was registered and the total players active
        return f"Player {player_name} registered\nTotal Players: {len(self.players)}\n"

    # This function queries all active players, looping through each player in the list and outputting their details
    # We tried to print as well the total players afterwards but it kept printing after each instance of a player so we removed it
    def query_players(self):
        response = "Players:\n"
        # There were multiple ways we tried to output the players to make it look presentable. We found that looping through each
        # name in the players list and outputting their info on separate lines worked. We'll have to incorporate handling for 
        # duplicate names, invalid players, etc.
        for player_name, details in self.players.items():
            response += (
                f"""{player_name}\n{details['address']}\nPlayer Port: {details['player port']}\nPeer Port: {details['peer port']}\nStatus: {details['status']}\n Game ID: {details['game ID']}\n\n"""
            )
        return response

    # Start game request handler that starts a game with all free players
    def start_game(self, request):
          dealer = request[1]
          holes = request[2]
          
          # This sets the game ID for the game being started then increments it by 1 for the next game created to have a different ID
          game_id = self.game_id
          self.game_id = self.game_id + 1
          
          # Grabs all free players and sets their status to in a game and saves their game ID
          for player_name, details in self.players.items():
            if details['status'] == 'free':
                self.players[player_name]['status'] = 'in game'
                self.players[player_name]['game ID'] = game_id
          
          # This saves games details for querying later on when a player queries games
          self.games[game_id] = {
                'dealer' : dealer,
                'holes' : holes,
                'status' : 'in play'
          }

          # This grabs all players being put into the game (based on specific game ID) and their details, then sends back to player (dealer) that requested
          response = "Players starting game:\n"
          for player_name, details in self.players.items():
            if details['status'] == 'in game' & details['game ID'] == game_id:
                response += (
                f"""{player_name}\n{details['address']}\nPlayer Port: {details['player port']}\nPeer Port: {details['peer port']}\nStatus: {details['status']}\n Game ID: {details['game ID']}\n\n"""
                )
            else:
                  continue
          return response

    # This function gathers the total games active and returns it. There is no game setup implementation so games will always 
    # return 0
    def query_games(self):
        response = f"Running Games: {len(self.games)}\n"
        return response

    # This function deregisters a player given the parameters in the function call. The del command is used to remove the instance
    # and the player is removed from the list. The player that is deregistered and the total players after the removal is returned.
    def deregister_player(self, request):
        player_name = request[1]
        del self.players[player_name]
        return f"Player {player_name} deregistered\nTotal Players: {len(self.players)}\n"
    
    # This function handles each individual player request messages. It can handle register, query players, query games, and deregister
    # The response when it gets the output back from the function called is then also sent back to the player that sent the request.
    def handle_client(self, conn, addr, tracker):
        # The below line decodes the message from the player and splits it by space into an array
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
                    # This line has no effect, but may be used to exit server in the future
                    connected = False
        # The below line sends the output reponse back to the player that sent the inital request
        tracker.sendto(response.encode(FORMAT), addr)

# The below line initiates a new instance of the server
tracker = Tracker()
print("SERVER STARTED")
# The below line starts the server using the start function
tracker.start()
