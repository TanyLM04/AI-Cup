import numpy as np
from constants import BOARD_SIZE, WIN_LINE_LENGTH, BLANK_SYMBOL

class nearSighted:
    def __init__(self, agent_symbol, blank_symbol, opponent_symbol, depth=2):
        self.name = __name__
        self.agent_symbol = agent_symbol
        self.blank_symbol = blank_symbol
        self.opponent_symbol = opponent_symbol
        self.depth = depth
        self.move_counter = 0


    def play(self, board):
        possible_moves = self.get_possible_moves(board)
        if not possible_moves:
            return None
        if np.count_nonzero(board) == 0:
            return (7, 7)
        
        best_move = None
        best_value = -float('inf')
        
        for move in possible_moves:
            new_board = board.copy()
            new_board[move] = self.agent_symbol
            if self.is_win(new_board, move, self.agent_symbol):
                value = 1000000
            else:
                value = self.evaluate(board)
            
            if value > best_value:
                best_value = value
                best_move = move
            print(value)
        return best_move
    
    def get_possible_moves(self,    board):
        if np.count_nonzero(board) == 0:  # First move: play center
            return (7, 7)
        candidates = set() # AVOID DUPLICATES
        for x in range(BOARD_SIZE):
            for y in range(BOARD_SIZE):
                if board[x, y] != 0: # IF SQUARE NOT EMPTY
                    for dx in range(-2, 3):
                        for dy in range(-2, 3): # 5x5 SQUARE (OPTIMIZES SEARCH) | delta x, and delta y
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE 
                                and board[nx, ny] == BLANK_SYMBOL):
                                candidates.add((nx, ny))
        return list(candidates)
    
    def minimax_value(self, board, depth, maximizing_player):
        possible_moves = self.get_possible_moves(board)
        if depth == 0 or not possible_moves:
            return self.evaluate(board)
        
        if maximizing_player:
            best_value = -float('inf')
            for move in possible_moves:
                new_board = board.copy()
                new_board[move] = self.agent_symbol
                if self.is_win(new_board, move, self.agent_symbol):
                    value = 1000000
                else:
                    value = self.minimax_value(new_board, depth - 1, False)
                
                best_value = max(best_value, value)
            return best_value
            
        else:
            best_value = float('inf')
            for move in possible_moves:
                new_board = board.copy()
                new_board[move] = self.opponent_symbol
                if self.is_win(new_board, move, self.opponent_symbol):
                    value = -1000000
                else:
                    value = self.minimax_value(new_board, depth - 1, True)
                
                best_value = min(best_value, value)
            return best_value
    
    def is_win(self, board, move, player):
        i, j = move
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # Horizontal, vertical, diagonals
        for dx, dy in directions:
            count = 1  # Include the current stone
            step = 1
            while (0 <= i + step * dx < BOARD_SIZE and 
                    0 <= j + step * dy < BOARD_SIZE and 
                    board[i + step * dx, j + step * dy] == player):
                count += 1
                step += 1
            step = 1
            while (0 <= i - step * dx < BOARD_SIZE and 
                    0 <= j - step * dy < BOARD_SIZE and 
                    board[i - step * dx, j - step * dy] == player):
                count += 1
                step += 1
            if count >= WIN_LINE_LENGTH:
                return True
        return False
    
    def get_pattern_id(self, i, j, dx, dy, player):
        """Create a unique identifier for a pattern"""
        return f"{player}-{i}-{j}-{dx}-{dy}"
    
    def evaluate(self, board):
        pattern_scores = {
            (4, 2): 100000,
            (4, 1): 10000,
            (4, 0): 0,
            (3, 2): 1000,
            (3, 1): 500,
            (3, 0): 0,
            (2, 2): 100,
            (2, 1): 50,
            (2, 0): 0
        }
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        agent_score = 0
        opponent_score = 0
        counted_patterns = set()
        
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i, j] == 0:
                    continue
                player = board[i, j]
                
                for dx, dy in directions:
                    # Create a unique identifier for this pattern line
                    pattern_id = self.get_pattern_id(i, j, dx, dy, player)
                    if pattern_id in counted_patterns:
                        continue  # Skip if we've already scored this pattern

                    # Check if current cell starts a new sequence
                    prev_i, prev_j = i - dx, j - dy
                    if (0 <= prev_i < BOARD_SIZE and 0 <= prev_j < BOARD_SIZE and 
                        board[prev_i, prev_j] == player):
                        continue  # Not the start of a sequence
                    
                    # Count consecutive stones and track pattern
                    count = 1
                    step = 1
                    pattern_positions = [(i, j)]
                    
                    while (0 <= i + step * dx < BOARD_SIZE and 
                        0 <= j + step * dy < BOARD_SIZE and 
                        board[i + step * dx, j + step * dy] == player):
                        pattern_positions.append((i + step * dx, j + step * dy))
                        count += 1
                        step += 1
                    
                    # Mark all positions in this pattern as counted for this direction
                    for pos in pattern_positions:
                        pos_pattern_id = self.get_pattern_id(pos[0], pos[1], dx, dy, player)
                        counted_patterns.add(pos_pattern_id)
                    
                    
                    pattern_start = (i - dx, j - dy)
                    pattern_end = (i + step * dx, j + step * dy)
                    
                    open_ends = 0
                    for x, y in [pattern_start, pattern_end]:
                        if (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and board[x, y] == 0):
                            open_ends += 1
                    
                    if count >= 5:
                        return 1000000 if player == self.agent_symbol else -1000000
                    
                    score = pattern_scores.get((count, open_ends), 0)
                    if player == self.agent_symbol:
                        agent_score += score
                    else:
                        opponent_score += score
        
        return agent_score - opponent_score