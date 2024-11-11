from battleship.ship import Ship, ShipFactory
from battleship.convert import CellConverter

class Board:
    """ Class representing the board of the player. 
            
    Acts as an interface between the player and its ships.
    """
    def __init__(self, ships=None, size=(10,10), 
                ships_per_length=None, should_validate=True):
        """ Initialises a Board given a list of ships. 
        
        Args:
            ships (list[Ship]): List of ships for the board. Auto-generates 
                ships if not given.
            size (tuple[int, int]): (width, height) of the board (in terms of 
                number of cells). Defaults to (10, 10).
            ships_per_length (dict): A dict with the length of ship as keys and
                the count as values. Defaults to 1 ship each for lengths 1-5.
            should_validate (bool): Should the constructor validate the 
                arrangements of the ships on the board? Defaults to True.
                
        Raises:
            ValueError if the number of ships is False
        """
        self.width = size[0]
        self.height = size[1]
        
        # Set of cells that have been attacked
        # Used for visualising the board
        self.marked_cells = set()
        
        # Dict storing the specified number of ships per length
        # Mainly used for validating the board configuration
        self.ships_per_length = {}
        if ships_per_length is not None:
            self.ships_per_length = {length: freq
                for (length, freq) in ships_per_length.items() 
                if length > 0 and freq > 0}
        else:
            self.ships_per_length.update({1: 1, 2: 1, 3: 1, 4: 1, 5: 1})
        
        if ships is None:
            # Auto-generate ships for the board if not specified
            # You will complete this method in Task 3
            ship_factory = ShipFactory(board_size=size, 
                                       ships_per_length=self.ships_per_length)
            self.ships = ship_factory.generate_ships()
        else:
            self.ships = ships
        
        if should_validate:
            self.validate_ships()
    
    def validate_ships(self):
        """ Validate the ship arrangements on the board.
        
        Make sure that:
        - the number of ships created are correct
        - ships are not too close to each other
        
        Raises:
            ValueError if there are any invalid ship arrangements
        """
        if not self.are_ships_within_bounds():
            raise ValueError("Some ships are in cells beyond the bounds of "
                "the board.")
        
        if not self.are_ship_lengths_correct():
            total_ships = sum(self.ships_per_length.values())
            error_message = f"There should be {total_ships} ships in total:\n"
            for ship_length, ship_count in self.ships_per_length.items():
                error_message += f" - {ship_count} of length {ship_length}\n"
            raise ValueError(error_message)
        
        if self.are_ships_too_close():
            raise ValueError("Some ships are too close to each other.")
            
    def are_ship_lengths_correct(self): 
        """ Check whether the number of ships are correct per length.
        
        Returns:
            bool : return True if there is a mismatch between the number of 
                ships required vs the number of ships available
        """
        ships_per_length = dict()
        for ship in self.ships:
            length = ship.length()
            ships_per_length[length] = ships_per_length.get(length, 0) + 1
        return ships_per_length == self.ships_per_length
    
    def are_ships_within_bounds(self): 
        """ Check whether all ships occupy valid cells within the board.
        
        Returns:
            bool : return True if all ships occupy valid cells on the board. 
                Return False otherwise.
        """
        if len(self.ships) != 0:
            for ship in self.ships:
                if ship.x_start < 1 or ship.x_end > self.width or ship.y_start < 1 or ship.y_end > self.height:
                    return False
        return True
        
    def are_ships_too_close(self):
        """ Check whether there is at least a pair of ships that are too close.
        
        Returns:
            bool : return True if and only if there is at least a pair of 
                ships on the board that are near each other. Returns False 
                otherwise
        """
        for i in range(len(self.ships)):
            for j in range(i+1, len(self.ships)):
                if self.ships[i].is_near_ship(self.ships[j]):
                    return True
        return False
        
    def have_all_ships_sunk(self):
        """ Check whether all ships have sunk.
        
        Returns:
            bool : return True if all ships on the board have sunk.
               return False otherwise.
        """
        for ship in self.ships:
            if ship.has_sunk() == False:
                return False
        return True
    
    def is_ship_hit(self, cell):
        """ Check if there is a ship at the cell that has been hit.
        
        Args:
            cell (tuple[int, int]): Coordinates of the cell to check.
            
        Returns:
            bool: True if a ship occupies the cell and has been hit there, else False.
        """
        for ship in self.ships:
            if ship.is_occupying_cell(cell) and cell in ship.damaged_cells:
                return True
        return False

    def has_ship_sunk(self, cell):
        """ Check if the ship at a particular cell has sunk.
        
        Args:
            cell (tuple[int, int]): Coordinates of the cell.
            
        Returns:
            bool: True if the ship occupying the cell has sunk, else False.
        """
        for ship in self.ships:
            if ship.is_occupying_cell(cell) and ship.has_sunk():
                return True
        return False

    
    def is_attacked_at(self, cell):
        """ Board is attacked at an (x, y) cell coordinate.
        
        The board experiences an attack at cell position (x, y).
        - if there is no ship at that position -> nothing happens
        - if there is a ship at that position -> the ship is damaged at that 
          coordinate

        Args:
            cell (tuple[int, int]): (x, y) cell coordinates targetted
            
        Returns:
            tuple : (is_ship_hit, has_ship_sunk) where
                - is_ship_hit is True if and only if the cell is occupied by a 
                  ship (False otherwise)
                - has_ship_sunk is True if and only if the attack made the ship 
                  sink (False otherwise)
        """
        # Mark the cell that has been attacked for visualisation purposes
        self.marked_cells.add(cell)
        
        is_ship_hit = False
        has_ship_sunk = False

        for ship in self.ships:
            if ship.is_occupying_cell(cell):
                is_ship_hit = True
                ship.receive_damage(cell)
                has_ship_sunk = ship.has_sunk()
                return is_ship_hit, has_ship_sunk
        return is_ship_hit, has_ship_sunk

        
    def print(self, show_ships=False):
        """ Visualise the board on the terminal.
        
        Args:
            show_ships (bool): Shows the ships on the board. Defaults to False. 
            
        Returns:
            None
        """
        array_board = self._build_array(show_ships=show_ships)
        board_str = self._array_to_str(array_board)
        print(board_str)

    def _build_array(self, show_ships=False):
        """ Generate an array representation of the Board for visualisation."""
        array_board = [[' ' for _ in range(self.width)] 
                       for _ in range(self.height)]

        for x_shot, y_shot in self.marked_cells:
            array_board[y_shot - 1][x_shot - 1] = 'O'

        for ship in self.ships:
            if ship.has_sunk():
                for x_ship, y_ship in ship.cells:
                    array_board[y_ship - 1][x_ship - 1] = '$'
                continue
                
            if show_ships:
                for x_ship, y_ship in ship.cells:
                    array_board[y_ship - 1][x_ship - 1] = 'S'

            for x_ship, y_ship in ship.damaged_cells:
                array_board[y_ship - 1][x_ship - 1] = 'X'
        
        return array_board
    
    def _array_to_str(self, array_board):
        """ Convert an array representation of the Board to string 
            representation to facilitate visualisation.
        """
        list_lines = []

        array_first_line = [chr(code + CellConverter.UPPERCASE_OFFSET) 
                            for code in range(1, self.width + 1)]
        first_line = ' ' * 6 + (' ' * 5).join(array_first_line) + ' \n'

        for index_line, array_line in enumerate(array_board, 1):
            number_spaces_before_line = 2 - len(str(index_line))
            space_before_line = number_spaces_before_line * ' '
            list_lines.append(f'{space_before_line}{index_line} |  ' 
                + '  |  '.join(array_line) + '  |\n')

        line_dashes = '   ' + '-' * 6 * self.width + '-\n'

        board_str = (first_line + line_dashes + line_dashes.join(list_lines) 
                     + line_dashes)

        return board_str


if __name__ == '__main__':
    # SANDBOX for you to play and test your methods

    ships = [
        Ship(start=(3, 1), end=(3, 5)),  # length = 5
        Ship(start=(9, 7), end=(9, 10)),  # length = 4
        Ship(start=(1, 9), end=(3, 9)),  # length = 3
        Ship(start=(5, 2), end=(6, 2)),  # length = 2
        Ship(start=(8, 3), end=(8, 3)),  # length = 1
    ]
    
    # Board with manually specified ships
    board = Board(ships=ships)
    print(board.ships)
    board.print(show_ships=True)
    is_ship_hit, is_ship_sunk = board.is_attacked_at((3, 4))
    print(is_ship_hit, is_ship_sunk)
    
    # Automatic board
    board = Board()
    print(board.ships)
    board.print(show_ships=True)
    