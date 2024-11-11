import random

from battleship.board import Board
from battleship.convert import CellConverter

class Player:
    """ Class representing the player
    """
    count = 0  # for keeping track of number of players
    
    def __init__(self, board=None, name=None):
        """ Initialises a new player with its board.

        Args:
            board (Board): The player's board. If not provided, then a board
                will be generated automatically
            name (str): Player's name
        """
        
        if board is None:
            self.board = Board()
        else:
            self.board = board
        
        Player.count += 1
        if name is None:
            self.name = f"Player {self.count}"
        else:
            self.name = name
    
    def __str__(self):
        return self.name
    
    def select_target(self):
        """ Select target coordinates to attack.
        
        Abstract method that should be implemented by any subclasses of Player.
        
        Returns:
            tuple[int, int] : (x, y) cell coordinates at which to launch the 
                next attack
        """
        raise NotImplementedError
    
    def receive_result(self, is_ship_hit, has_ship_sunk):
        """ Receive results of latest attack.
        
        Player receives notification on the outcome of the latest attack by the 
        player, on whether the opponent's ship is hit, and whether it has been 
        sunk. 
        
        This method does not do anything by default, but can be overridden by a 
        subclass to do something useful, for example to record a successful or 
        failed attack.
        
        Returns:
            None
        """
        return None
    
    def has_lost(self):
        """ Check whether player has lost the game.
        
        Returns:
            bool: True if and only if all the ships of the player have sunk.
        """
        return self.board.have_all_ships_sunk()


class ManualPlayer(Player):
    """ A player playing manually via the terminal
    """
    def __init__(self, board, name=None):
        """ Initialise the player with a board and other attributes.
        
        Args:
            board (Board): The player's board. If not provided, then a board
                will be generated automatically
            name (str): Player's name
        """
        super().__init__(board=board, name=name)
        self.converter = CellConverter((board.width, board.height))
        
    def select_target(self):
        """ Read coordinates from user prompt.
               
        Returns:
            tuple[int, int] : (x, y) cell coordinates at which to launch the 
                next attack
        """
        print(f"It is now {self}'s turn.")

        while True:
            try:
                coord_str = input('coordinates target = ')
                x, y = self.converter.from_str(coord_str)
                return x, y
            except ValueError as error:
                print(error)


class RandomPlayer(Player):
    """ A Player that plays at random positions.

    However, it does not play at the positions:
    - that it has previously attacked
    """
    def __init__(self, name=None):
        """ Initialise the player with an automatic board and other attributes.
        
        Args:
            name (str): Player's name
        """
        # Initialise with a board with ships automatically arranged.
        super().__init__(board=Board(), name=name)
        self.tracker = set()

    def select_target(self):
        """ Generate a random cell that has previously not been attacked.
        
        Also adds cell to the player's tracker.
        
        Returns:
            tuple[int, int] : (x, y) cell coordinates at which to launch the 
                next attack
        """
        target_cell = self.generate_random_target()
        self.tracker.add(target_cell)
        return target_cell

    def generate_random_target(self):
        """ Generate a random cell that has previously not been attacked.
               
        Returns:
            tuple[int, int] : (x, y) cell coordinates at which to launch the 
                next attack
        """
        has_been_attacked = True
        random_cell = None
        
        while has_been_attacked:
            random_cell = self.get_random_coordinates()
            has_been_attacked = random_cell in self.tracker

        return random_cell

    def get_random_coordinates(self):
        """ Generate random coordinates.
               
        Returns:
            tuple[int, int] : (x, y) cell coordinates at which to launch the 
                next attack
        """
        x = random.randint(1, self.board.width)
        y = random.randint(1, self.board.height)
        return (x, y)


class AutomaticPlayer(Player):
    """ Player playing automatically using a strategy."""
    def __init__(self, name=None):
        """ Initialise the player with an automatic board and other attributes.
        
        Args:
            name (str): Player's name
        """
        # Initialise with a board with ships automatically arranged.
        super().__init__(board=Board(), name=name)
        self.tracker = set()  # Set to track all attempted cells
        self.dont_choose = set()  # Cells to avoid, especially around sunk ships
        self.last_hit = None
        self.current_ship_info = {
            'active': False,
            'start': None,
            'end': None,
            'direction': None,
            'length': 0,
            'hits': [],
            'start_found': False,
            'end_found': False
        }

    def receive_result(self, is_ship_hit, has_ship_sunk):
        """Records the result of the last attack and updates strategy."""
        # Reset if the ship has sunk
        if has_ship_sunk:
            self.update_current_ship(self.last_hit)
            self.dont_hit_nearby_cells() 
            self.reset_current_ship()

        elif is_ship_hit:
            # Initialize ship to focus on hitting
            if not self.current_ship_info['active']:
                self.initialise_ship(self.last_hit)
            else:
                self.update_current_ship(self.last_hit)

        else:  #miss
            if self.current_ship_info['active']:
                if not self.current_ship_info['direction']:
                    #direction is still unknown; do not lock into one direction yet
                    self.tracker.add(self.last_hit)  # Record the miss
                else:
                    self.found_end(self.last_hit)  #process end of ship if direction is known
            else:
                #it was a miss and no ship was active, just record the miss
                self.tracker.add(self.last_hit)
                

    def initialise_ship(self, cell):
        """Initialise a ship to find based on a new hit."""
        self.current_ship_info['active'] = True
        self.current_ship_info['start'] = cell
        self.current_ship_info['end'] = cell
        self.current_ship_info['hits'].append(cell)


    def update_current_ship(self, cell):
        """Update the current ship's boundaries and orientation."""
        direction = self.current_ship_info['direction']
        self.current_ship_info['hits'].append(cell)
        if not direction:
        #if ship is sunk on first hit
            if len(self.current_ship_info['hits']) == 1:
                self.current_ship_info['start'] = cell
                self.current_ship_info['end'] = cell

        #if direction is unknown (length 1), update based on the latest hit cell
            elif cell[0] == self.current_ship_info['start'][0]:  #vertical alignment
                direction = 'v'
            elif cell[1] == self.current_ship_info['start'][1]:  #horizontal alignment
                direction = 'h'
            self.current_ship_info['direction'] = direction

        #extend boundaries based on direction
        if direction == 'v': 
            if cell[1] < self.current_ship_info['start'][1]:  
                self.current_ship_info['start'] = cell
            else: 
                self.current_ship_info['end'] = cell

        else: 
            if cell[0] < self.current_ship_info['start'][0]:  
                self.current_ship_info['start'] = cell
            else: 
                self.current_ship_info['end'] = cell
        


    def dont_hit_nearby_cells(self):
        """Records cells nearby ship to not choose."""
        x1 = self.current_ship_info['start'][0]
        x2 = self.current_ship_info['end'][0]
        y1 = self.current_ship_info['start'][1]
        y2 = self.current_ship_info['end'][1]

        for x in range(x1-1,x2+2):
            for y in range(y1-1,y2+2):
                self.dont_choose.add((x,y))


    def reset_current_ship(self):
        """Resets the current ship information."""
        self.current_ship_info = {
            'active': False,
            'start': None,
            'end': None,
            'direction': None,
            'hits': [],
            'start_found': False,
            'end_found': False
        }

    def found_end(self, cell):
        if self.current_ship_info['direction'] == 'v':
            if cell[1]<self.current_ship_info['start'][1]:
                self.current_ship_info['start_found'] = True
            elif cell[1]>self.current_ship_info['end'][1]:
                self.current_ship_info['end_found'] = True

        elif self.current_ship_info['direction'] == 'h':
            if cell[0]<self.current_ship_info['start'][0]:
                self.current_ship_info['start_found'] = True
            elif cell[0]>self.current_ship_info['end'][0]:
                self.current_ship_info['end_found'] = True

    
    def choose_randomly(self):
        """randomly selects cell, from available."""
        x = random.randint(1, self.board.width)
        y = random.randint(1, self.board.height)
        while (x,y) in self.tracker or (x,y) in self.dont_choose:
            x = random.randint(1, self.board.width)
            y = random.randint(1, self.board.height)
        return (x,y)
    

    def in_bounds(self, cell):
        """
        Checks whether a given cell is in bounds.
        Args:
            cell : cell to assess
        
        Return:
            Bool : True if in bounds
        """
        x, y = cell
        return 1 <= x <= self.board.width and 1 <= y <= self.board.height 

        
    def check_above(self):
        x,y = self.current_ship_info['start']
        y -= 1
        cell = (x,y)
        if not self.in_bounds(cell) or cell in self.tracker or cell in self.dont_choose:
            return False
        return cell
    
    def check_below(self):
        x,y = self.current_ship_info['end']
        y += 1
        cell = (x,y)
        if not self.in_bounds(cell) or cell in self.tracker or cell in self.dont_choose:
            return False
        return cell
    
    def check_left(self):
        x,y = self.current_ship_info['start']
        x -= 1
        cell = (x,y)
        if not self.in_bounds(cell) or cell in self.tracker or cell in self.dont_choose:
            return False
        return cell
    
    def check_right(self):
        x,y = self.current_ship_info['end']
        x += 1
        cell = (x,y)      
        if not self.in_bounds(cell) or cell in self.tracker or cell in self.dont_choose:
            return False
        return cell
    
    def choose_around_cell(self):
        x, y = self.current_ship_info['start']
        for dx, dy in [(-1, 0), (0,-1), (1,0), (0,1)]:
                new_cell = (x + dx, y + dy)
                if self.in_bounds(new_cell) and new_cell not in self.tracker and new_cell not in self.dont_choose:
                    return new_cell

        
    def select_target(self):
        """ Select target coordinates to attack.
        
        Returns:
            tuple[int, int] : (x, y) cell coordinates at which to launch the 
                next attack
        """
        #chosen randomly if not currently searching for ship
        
        if not self.current_ship_info['active']:
            cell =  self.choose_randomly()

        
        #if currently searching for ship
        else:
            cell = False
            #if we have not found start of ship, (top/left) go that way
            if self.current_ship_info['direction'] == None:
                cell = self.choose_around_cell()

            elif self.current_ship_info['direction'] == 'h':
                if self.current_ship_info['start_found'] == False:
                    #go left
                    cell = self.check_left()
                    if not cell:
                        #if this is false weve found the edge or hit a previous empty cell so start has been found
                        self.current_ship_info['start_found'] == True
                        #so end must not be found otherwise it wouldve sunk, go that direction
                        cell = self.check_right()

                #if starts found search end 
                else:
                    cell = self.check_right()

            #direction must be vertical
            else: 
                if self.current_ship_info['start_found'] == False:
                    #go up
                    cell = self.check_above()
                    if not cell:
                        #if this is false weve found the edge or hit a previous empty cell so start has been found
                        self.current_ship_info['start_found'] == True
                        #so end must not be found otherwise it wouldve sunk, go that direction
                        cell = self.check_below()

                #if starts found search end 
                else:
                    cell = self.check_below()

        self.tracker.add(cell)
        self.last_hit = cell

        return cell