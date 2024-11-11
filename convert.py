class CellConverter:
    UPPERCASE_OFFSET = 64
    
    def __init__(self, board_size):
        self.board_size = board_size
    
    def to_str(self, cell):
        """ Convert (x,y) cell coordinates to string format (e.g. B1).
        
        Args: 
            cell (tuple[int, int]): (x, y) cell coordinates
        
        Returns:
            str : String representation of cell (e.g. "C3")
        """
        return chr(cell[0] + CellConverter.UPPERCASE_OFFSET) + str(cell[1])


    def from_str(self, cell_str):
        """ Convert cell position in string format (e.g. B1) to (x, y) coords.
        
        Args: 
            cell_str (str) : String representation of cell (e.g. "C3")
        
        Returns:
            cell (tuple[int, int]): (x, y) cell coordinates
        """
        cell_str = cell_str.strip()

        if not 2 <= len(cell_str) <= 3:
            raise ValueError(f"'{cell_str}' is an invalid position.")

        coord_1, coord_2 = cell_str[0], cell_str[1:]

        coord_1 = ord(coord_1) - CellConverter.UPPERCASE_OFFSET
        
        try:
            coord_2 = int(coord_2)
        except ValueError:
            raise ValueError(f"The position provided '{cell_str}' is not valid")
                        
        if not (0 < coord_1 <= self.board_size[0] and 
                0 < coord_2 <= self.board_size[1]):
            raise ValueError(f"The position provided '{cell_str}' is not valid")

        return coord_1, coord_2


if __name__ == '__main__':
    converter = CellConverter(board_size=(10, 10))
        
    cell = converter.from_str("J9")
    print(cell)
    assert cell == (10, 9)
    
    cell_str = converter.to_str((1, 1))
    print(cell_str)
    assert cell_str == "A1"