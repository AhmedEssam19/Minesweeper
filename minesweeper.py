import random


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence:
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if self.count == len(self.cells):
            return self.cells
        else:
            return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        self.cells.discard(cell)


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)
        self.add_neighbours_sentence(cell, count)

        updated = True
        # loop until there is nothing to be done by
        while updated:
            # Reset flag to false to track that there is something to be done or not
            updated = False

            # iterate over all possible pairs of sentence
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    # Infer new sentence if one sentence is subset of the other one
                    if sentence1 != sentence2 and len(sentence1.cells) > 1 and sentence1.cells < sentence2.cells:
                        # The inferred set with elements in the second set that are not in the first one.
                        # The inferred count is the second count minus the first
                        concluded_sentence = Sentence(sentence2.cells - sentence1.cells,
                                                      sentence2.count - sentence1.count)

                        # Add the new sentence to knowledge if it hadn't inferred before
                        if concluded_sentence not in self.knowledge:
                            self.knowledge.append(concluded_sentence)
                            updated = True

            # Infer mine cells or safe cells
            for sentence in self.knowledge:
                # Make a copy of known_mines not to modify the set while iterating over it
                known_mines = sentence.known_mines().copy()
                if len(known_mines) > 0:
                    for mine in known_mines:
                        self.mark_mine(mine)
                    updated = True

                # Make a copy of known_safes not to modify the set while iterating over it
                know_safes = sentence.known_safes().copy()
                if len(know_safes) > 0:
                    for safe_cell in know_safes:
                        self.mark_safe(safe_cell)
                    updated = True

    def add_neighbours_sentence(self, cell, count):
        """
        Determine neighbour cells of this
        :param cell: cell that is recently moved to
        :param count: number of mines around this cell
        """
        neighbour_cells = set()
        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Add the cell to neighbours if cell in bounds
                if 0 <= i < self.height and 0 <= j < self.width:
                    # Neglect cell that is mine and reduce count by 1
                    if (i, j) in self.mines:
                        count -= 1

                    # Neglect cell that is safe and add other cells
                    elif (i, j) not in self.safes:
                        neighbour_cells.add((i, j))

        # Add new sentence to knowledge
        self.knowledge.append(Sentence(neighbour_cells, count))

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # iterate over safe moves and return the first move that hasn't made yet
        for move in self.safes:
            if move not in self.moves_made:
                return move

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # When all the possible moves are made or mine, then there is no possible random move
        if len(self.moves_made) + len(self.mines) == self.height * self.width:
            return None

        # Choose random move tha haven't made yet
        while True:
            random_move = (random.randrange(self.height),
                           random.randrange(self.width))

            if random_move not in self.moves_made and random_move not in self.mines:
                return random_move
