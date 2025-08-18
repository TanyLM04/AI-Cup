import numpy as np
from constants import BOARD_SIZE, WIN_LINE_LENGTH, BLANK_SYMBOL

class AlphaBetaAgent:
    def __init__(self, agent_symbol, blank_symbol, opponent_symbol, depth=3):
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
        if np.count_nonzero(board) == 0:  # First move: play center
            return (7, 7)
        
        best_move = None
        best_value = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        for move in possible_moves:
            new_board = board.copy()
            new_board[move] = self.agent_symbol
            if self.is_win(new_board, move, self.agent_symbol):
                value = 1000000  # Instant win
            else:
                value = self.minimax_value(new_board, self.depth - 1, alpha, beta, False)
            if value > best_value: ## me hace ruido == 100000?
                best_value = value
                best_move = move
            alpha = max(alpha, best_value)
            if best_value >= beta or best_value == 1000000:
                break

        self.move_counter += 1
        print(f"""
value: {value}
alpha: {alpha}
beta: {beta}
                      """)
        return best_move
    
    def minimax_value(self, board, depth, alpha, beta, maximizing_player):
        possible_moves = self.get_possible_moves(board)
        if depth == 0 or not possible_moves:
            return self.evaluate(board)
        
        if maximizing_player: # if True it's AGENT's turn and if it is False it's opponent's turn
            best_value = -float('inf')
            for move in possible_moves:
                new_board = board.copy()
                new_board[move] = self.agent_symbol
                if self.is_win(new_board, move, self.agent_symbol):
                    value = 1000000
                else:
                    value = self.minimax_value(new_board, depth - 1, alpha, beta, False)
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if best_value >= beta or best_value == 1000000:
                    break
            return best_value
        else: # OPPONENT turn
            best_value = float('inf')
            for move in possible_moves:
                new_board = board.copy()
                new_board[move] = self.opponent_symbol
                if self.is_win(new_board, move, self.opponent_symbol):
                    value = -1000000
                else:
                    value = self.minimax_value(new_board, depth - 1, alpha, beta, True)
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if best_value <= alpha or best_value == -1000000:
                    break
            return best_value
        
    def get_possible_moves(self, board):
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
    
    def is_win(self, board, move, player):
        i, j = move
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]  # Horizontal, vertical, diagonals
        for dx, dy in directions:
            count = 1  # Include the current stone
            # Check positive direction
            step = 1
            while (0 <= i + step * dx < BOARD_SIZE and 
                    0 <= j + step * dy < BOARD_SIZE and 
                    board[i + step * dx, j + step * dy] == player):
                count += 1
                step += 1
            # Check negative direction
            step = 1
            while (0 <= i - step * dx < BOARD_SIZE and 
                    0 <= j - step * dy < BOARD_SIZE and 
                    board[i - step * dx, j - step * dy] == player):
                count += 1
                step += 1
            if count >= WIN_LINE_LENGTH:
                return True
        return False
    
    def evaluate(self, board):
        pattern_scores = { # NO VALUES FOR WIN SITUATIONS BECAUSE WE USE is_win() instead
            (4, 2): 100000,   # Open four
            (4, 1): 10000,    # Half-open four
            (4, 0): 0,        # Blocked four
            (3, 2): 1000,     # Open three
            (3, 1): 500,      # Half-open three
            (3, 0): 0,        # Blocked three
            (2, 2): 100,      # Open two
            (2, 1): 50,       # Half-open two
            (2, 0): 0,        # Blocked two
        }
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        agent_score = 0
        opponent_score = 0

        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                if board[i, j] == 0:
                    continue
                player = board[i, j]
                for dx, dy in directions:
                    # Check if current cell starts a new sequence
                    prev_i, prev_j = i - dx, j - dy
                    if (0 <= prev_i < BOARD_SIZE and 0 <= prev_j < BOARD_SIZE and 
                        board[prev_i, prev_j] == player):
                        continue  # Skip if not the start
                    
                    # Count consecutive stones
                    count = 1
                    step = 1
                    while (0 <= i + step * dx < BOARD_SIZE and 
                        0 <= j + step * dy < BOARD_SIZE and 
                        board[i + step * dx, j + step * dy] == player):
                        count += 1
                        step += 1
                    end1 = (i - dx, j - dy)  # Start end
                    end2 = (i + step * dx, j + step * dy)  # End after sequence
                    
                    # Check openness of ends
                    open_ends = 0
                    for x, y in [end1, end2]:
                        if (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
                            if board[x, y] == 0:
                                open_ends += 1
                    
                    # Win condition
                    if count >= 5:
                        if player == self.agent_symbol:
                            return 1000000
                        else:
                            return -1000000
                    
                    # Apply pattern scores
                    score = pattern_scores.get((count, open_ends), 0)
                    if player == self.agent_symbol:
                        agent_score += score
                    else:
                        opponent_score += score
        return min( agent_score - opponent_score)
