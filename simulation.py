from battleship.board import Board
from battleship.game import Game
from battleship.player import AutomaticPlayer, ManualPlayer, RandomPlayer
from battleship.ship import Ship, ShipFactory

class ManualVsManualSimulation:
    """ Play against your friend (or more likely yourself)! """
    def run(self):
        # Creating the ships MANUALLY for the 2 players Alice and Bob
        alice_ships = [
            Ship(start=(3, 1), end=(3, 5)),  # length = 5
            Ship(start=(9, 7), end=(9, 10)),  # length = 4
            Ship(start=(1, 9), end=(3, 9)),  # length = 3
            Ship(start=(5, 2), end=(6, 2)),  # length = 2
            Ship(start=(8, 3), end=(8, 3)),  # length = 1
        ]

        bob_ships = [
            Ship(start=(5, 8), end=(9, 8)),  # length = 5
            Ship(start=(5, 4), end=(8, 4)),  # length = 4
            Ship(start=(3, 1), end=(5, 1)),  # length = 3
            ShipFactory.create_ship_from_str(start="F10", end="G10"), # Another way of creating a Ship
            ShipFactory.create_ship_from_str(start="A4", end="A4"), # Another way of creating a Ship
        ]

        # Creating their boards
        alice_board = Board(alice_ships)
        bob_board = Board(bob_ships)

        # Creating the players
        alice = ManualPlayer(alice_board, name="Alice")
        bob = ManualPlayer(bob_board, name="Bob")

        # Creating and launching the game
        game = Game(player1=alice, player2=bob)
        game.play()


class ManualVsRandomSimulation:
    """ Try to defeat a RandomPlayer! """
    def run(self):
        # Creating the ships MANUALLY for the 2 players Alice and Bob
        alice_ships = [
            Ship(start=(3, 1), end=(3, 5)),  # length = 5
            Ship(start=(9, 7), end=(9, 10)),  # length = 4
            Ship(start=(1, 9), end=(3, 9)),  # length = 3
            Ship(start=(5, 2), end=(6, 2)),  # length = 2
            Ship(start=(8, 3), end=(8, 3)),  # length = 1
        ]

        # Creating a manual player
        alice_board = Board(alice_ships)
        alice = ManualPlayer(alice_board, name="Alice (Manual)")
        
        # Creating a random player
        bob = RandomPlayer(name="Bob (Random)")

        # Creating and launching the game
        game = Game(player1=alice, player2=bob)
        game.play()


class RandomVsRandomSimulation:
    """ Two RandomPlayers battling it out! Whose will have the better luck? """
    def run(self):
        # Creating two random players
        alice = RandomPlayer(name="Alice (Random)")
        bob = RandomPlayer(name="Bob (Random)")

        # Creating and launching the game
        game = Game(player1=alice, player2=bob)
        game.play()


class ManualVsAutomaticSimulation:
    """ Play against your AI player! """
    def run(self):
        # Creating a manual player with automatically generated board
        board = Board()
        alice = ManualPlayer(board=board, name="Alice (Manual)")
        
        # Creating a manual player
        bob = AutomaticPlayer(name="Bob (Automatic)")

        # Creating and launching the game
        game = Game(player1=alice, player2=bob)
        game.play()


class RandomVsAutomaticSimulation:
    """ A RandomPlayer vs your smarter AI player! """
    def run(self):
        # Creating one random player and one AI player
        alice = RandomPlayer(name="Alice (Random)")
        bob = AutomaticPlayer(name="Bob (Automatic)")

        # Creating and launching the game
        game = Game(player1=alice, player2=bob)
        game.play()


class AutomaticVsAutomaticSimulation:
    """ Get your AI players to battle each other! """
    def run(self):
        # Creating two AI players
        alice = AutomaticPlayer(name="Alice (Automatic)")
        bob = AutomaticPlayer(name="Bob (Automatic)")

        # Creating and launching the game
        game = Game(player1=alice, player2=bob)
        game.play()
