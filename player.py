# CSE 434 
# Fall 2024
# Socket Project
# Group 76
# Caleb Blackmon and Gursharan Singh
# Reference video used for Socket Programming in Python https://www.youtube.com/watch?v=3QiPPX-KeSc

import socket
import threading
import random

# This prompts the user to save the IP address of the player
SERVER = input("IP Address: ")
# Used for uniform decoding of messages to utf-8
FORMAT = 'utf-8'

# The below lines setup the standard 52 card deck
card_num = ['A', '2', '3', '4', '5', '6', '7','8', '9', '10', 'J', 'Q', 'K']
card_type = ['Spade', 'Diamond', 'Club', 'Heart']

# This uses the socket library to create a socket object using IPv4 and UDP structure
player_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# This creates the peer communication socket
peer_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Below commands prompt the user to enter info that will be used to register player later on
player_name = input("Player Name: ")
tracker_addr = input("Tracker Address: ")
# For these prompts we had to convert to int because it was messing up the sending of messages from
# player to tracker using the strings 
tracker_port = int(input("Tracker Port: "))
player_port = int(input("Player Port: "))
peer_port = int(input("Peer Port: "))

# Additional functionality added for peer to peer communication
peer_socket.bind((SERVER, peer_port))

# The class Player is used to create an instance of a player with the above features
class Player:

    # For this instance of the player, the features of the player are saved to variables using self identifier
    def __init__(self,player_name,tracker_addr,tracker_port, player_port, peer_port):
        self.player_name = player_name
        self.tracker_addr = tracker_addr
        self.tracker_port = tracker_port
        self.player_port = player_port
        self.peer_port = peer_port
        self.game_id = None
        self.cards = []

    # This function registers a new player with the player name, port, and peer port that the user enters 
    # when first running program. The message of register information is sent to the send_msg function to then 
    # send the command to the tracker.
    def register(self):
        message = f"register {self.player_name} {self.player_port} {self.peer_port}"
        self.send_msg(message)

    # This function querys all players registered. The message query players is sent to the send_msg function to 
    # then prompt the tracker to display all players.
    def query_players(self):
        message = "query players"
        self.send_msg(message)

    def start_game(self, holes):
        message = f"start game {self.player_name} {holes}"
        
        # Putting send msg function details right in this function
        player_socket.sendto(message.encode(), (self.tracker_addr, self.tracker_port))
        conn, _ = player_socket.recvfrom(2048)
        response = conn.decode(FORMAT)
        print(f"{conn.decode(FORMAT)}")

        # This grabs all players that will be starting the game from the response from the tracker
        # Also cycles through the lines from the response from the tracker to accurately break into parts using
        # a for loop.
        players = {}
        lines = response.splitlines()

        # Based on format of response from tracker, the for loop parts breakdown has to be setup parsing on 
        # different identifiers
        # This for loop skips the first line since it is just the header and not player data
        # Reference used for split/strip technique https://www.youtube.com/watch?v=qGAY-YGJr2U
        for i in range(1, len(lines), 7):
            player_name = lines[i].strip()
            player_ip = lines[i+1].strip()
            player_port = lines[i + 2].split(":")[1].strip()
            peer_port = lines[i + 3].split(":")[1].strip()
            players[player_name] = {'player ip': player_ip, 'player port': player_port, 'peer port': peer_port}

        # The players starting the game are dealt their cards using the deal_cards function
        self.deal_cards(players)


    # This function calls the end_game function in the tracker file
    def end_game(self, game_id):
        message = f"end game {game_id}"
        self.send_msg(message)
        print(f"Game {game_id} has ended.")

    # When called in the start_game function, this function deals cards to those specific players starting a game
    # Their hands are then sent to them
    def deal_cards(self, players):
        deck = [(type, num) for type in card_type for num in card_num]
        random.shuffle(deck)

        # For each player, they are looped through popping from the top of the deck until they each have 6 cards
        player_hands = {player: [deck.pop() for _ in range(6)] for player in players}
        
        # This for loop loops through each player and the dealer sends them their hand through their peer socket connection
        for player, hand in player_hands.items():
            if player == self.player_name:
                self.cards = hand
                print(f"Your hand: {hand}")
            else:
                peer_ip = players[player]['player ip']
                peer_port = players[player]['peer port']
                peer_socket.sendto(f"Your hand: {hand}".encode(FORMAT), (peer_ip, int(peer_port)))

    # This function querys all games started. The message query games is sent to the send_msg function to 
    # then prompt the tracker to display the total games running at the moment. Game setup is not currently implemented
    # so response will always be 0 games.
    def query_games(self):
        message = "query games"
        self.send_msg(message)

    # This function deregisters the current player and exits program from running. The message deregister with the player name
    # is sent to the send_msg command to prompt tracker to degregister the player
    def deregister(self):
        message = f"deregister {self.player_name}"
        self.send_msg(message)

    # This function sends the message provided by the above the functions to the tracker.
    def send_msg(self, message):
        player_socket.sendto(message.encode(), (self.tracker_addr, self.tracker_port))
        # For the below line, we orginally had conn, addr like usual but it was erroring and we found online that we should use
        # conn, _ instead. It works, but we don't totally understand why at the moment or how it may effect the rest of the
        # implementation of this project.
        conn, _ = player_socket.recvfrom(2048)
        # The below line prints the response from the tracker
        print(f"{conn.decode(FORMAT)}")

# This line creates a new instance of the player using prompts at beginning of program
player = Player(player_name, tracker_addr, tracker_port, player_port, peer_port)

# The below lines are the menu prompts for the player. They can select 1, 2, 3, or 4 which have corresponding functions to call
# In selection 4 which is deregister, connected then becomes false which exits the program
# The option 0 is also a valid option that exits the program and was used for testing when the code would hang or 
# when we'd need to exit
connected = True
while connected:
        ms = input("\nSelect Your Choice!\n1. Register\n2. Query Players\n3. Start Game\n4. End Game\n5. Query Games\n6. Deregister\n: ")
        if ms == "0":
            exit()
        elif ms == "1":
            #name = input("Name: ")
            player.register()
        elif ms == "2":
            player.query_players()
        elif ms == "3":
            holes = input("Number of Holes: ")
            player.start_game(holes)
        elif ms == "4":
            game_id = int(input("Game to end: "))
            player.end_game(game_id)
        elif ms == "5":
            player.query_games()
        elif ms == "6":
            player.deregister()
            connected = False
        else:
            print("Invalid Selection\n")
