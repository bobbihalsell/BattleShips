import random

from battleship.convert import CellConverter

class Game:
    """ Game class for performing game simulations.
    
    General rules of the game are defined in this class. For example:
    - if a ship is hit, the attacker has the right to play another time.
    - if all the opponent's ships have been sunk, the game stops, 
      and the results are printed
    """

    def __init__(self, player1, player2):
        """ Initialises a game.
        
        Args:
            player1 (Player): First player
            player2 (Player): Second player
        """
        self.player1 = player1
        self.player2 = player2
        
        self.converter = CellConverter((player1.board.width, 
                                        player1.board.height))
    
    def play(self):
        """ Simulates an entire game. 
        
        Prints out the necessary information (boards without ships, 
        positions under attack...)
        """
        attacker, opponent = self.select_starting_player()
        print(f"{attacker} starts the game.")
            
        # Simulates the game, until a player has lost
        while not self.player1.has_lost() and not self.player2.has_lost():
            self._print_turn_divider()
            
            is_ship_hit = None

            # If an opponent's ship is hit, the player is allowed to play 
            # another time.
            while is_ship_hit is None or is_ship_hit:
                self.show_opponent_board(opponent, attacker)

                # Attacker selects a target cell to attack
                target_cell = attacker.select_target()
                print(f"{attacker} attacks {opponent} "
                    f"at position {self.converter.to_str(target_cell)}")
                
                # Opponent gives outcome
                is_ship_hit, has_ship_sunk  = opponent.board.is_attacked_at(
                                                  target_cell)

                # Game manager announces outcome
                self.announce_turn_outcome(attacker, opponent, is_ship_hit, 
                                           has_ship_sunk)
                
                # Attacker records outcome
                attacker.receive_result(is_ship_hit, has_ship_sunk)
                
                # Game over if either player has lost
                if self.player1.has_lost() or self.player2.has_lost():
                    break

                if is_ship_hit:
                    self._print_divider()

            # Players swap roles
            attacker, opponent = opponent, attacker  

        # Show final results
        self._print_final_results()
        
    def select_starting_player(self):
        """ Selects a player to start at random. """
        # Chooses the player to start first
        if random.choice([True, False]):
            attacker = self.player1
            opponent = self.player2
        else:
            attacker = self.player2
            opponent = self.player1
            
        return attacker, opponent
    
    def show_opponent_board(self, opponent, attacker):  
        """ Displays the opponent's board.
        
        Args:
            opponent (Player)
            attacker (Player)
        """    
        print(f"Here is the current state of {opponent}'s board before "
            f"{attacker}'s attack:\n")
        opponent.board.print(show_ships=False)
                
    def announce_turn_outcome(self, attacker, opponent, is_ship_hit, 
                          has_ship_sunk): 
        """ Print out messages given the outcome of an attack.
        
        Args:
            attacker (Player)
            opponent (Player)
            is_ship_hit (bool)
            has_ship_sunk (bool)
        """                              
        if has_ship_sunk:
            print(f"\nA ship of {opponent} HAS SUNK. "
                  f"{attacker} can play another time.")
        elif is_ship_hit:
            print(f"\nA ship of {opponent} HAS BEEN HIT. "
                  f"{attacker} can play another time.")
        else:
            print("\nMissed".upper())
            
    def _print_turn_divider(self):
        self._print_divider(newlines=5)
        self._print_divider(newlines=1)
        
    def _print_divider(self, newlines=0):
        print("-" * 75)
        for _ in range(newlines):
            print()
        
    def _print_final_results(self):
        self._print_turn_divider()
        print(f"Here is the final state of {self.player1}'s board:\n ")
        self.player1.board.print(show_ships=True)

        self._print_divider(newlines=1)
        print(f"Here is the final state of {self.player2}'s board:\n")
        self.player2.board.print(show_ships=True)

        self._print_divider(newlines=1)
        if self.player1.has_lost():
            print(f"--- {self.player2} WINS THE GAME ---")
        else:
            print(f"--- {self.player1} WINS THE GAME ---")
