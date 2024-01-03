import numpy as np

class GameState:

    def __init__(self):
        """__init__: defines a new chess game. checkmate and check are set to false"""

        self.board = np.array( # defining the board
        [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ])
        # variables/flags needed throughout the game
        self.white_to_move = True
        self.move_log = []
        self.checkmate = False
        self.stalemate = False
        self.in_check = False
        self.wK_pos = (7, 4)
        self.bK_pos = (0, 4)
        self.pins = []
        self.checks = []
        self.possible_en_passant = ()
        self.current_castle_rights = CastleRights(True, True, True, True)
        self.current_castle_rights_log = [CastleRights(self.current_castle_rights.wks, 
                                                       self.current_castle_rights.bks, 
                                                       self.current_castle_rights.wqs, 
                                                       self.current_castle_rights.bqs)]
        



    def make_move(self, move):
        """
        Function to make a move on the board. Does not return anything.
        """
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        # pawn promotion (automatically a queen right now)
        if move.pawn_promotion:
            if self.white_to_move:
                self.board[move.end_row][move.end_col] = "wQ"
            else:
                self.board[move.end_row][move.end_col] = "bQ"
        self.white_to_move = not self.white_to_move
        if move.piece_moved == "wK":
            self.wK_pos = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.bK_pos = (move.end_row, move.end_col)
        # en passant
        if move.en_passant:
            move.piece_captured = self.board[move.start_row][move.end_col]
            self.board[move.start_row][move.end_col] = "--"
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
            self.possible_en_passant = ((move.start_row + move.end_row) // 2, move.end_col)
        else:
            self.possible_en_passant = ()
        # castle
        if move.castle:
            if move.end_col - move.start_col == 2: # kingside castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]
                self.board[move.end_row][move.end_col + 1] = "--"
            elif move.end_col - move.start_col == -2: # queenside castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 2]
                self.board[move.end_row][move.end_col - 2] = "--"
        self.update_castle_rights(move)
        self.current_castle_rights_log.append(CastleRights(self.current_castle_rights.wks, 
                                                           self.current_castle_rights.bks, 
                                                           self.current_castle_rights.wqs, 
                                                           self.current_castle_rights.bqs))
        self.move_log.append(move)




    def undo_move(self):
        """
        Fucntion to undo a move made on the board. Does not return anything.
        """
        last_move = self.move_log.pop()
        self.board[last_move.start_row][last_move.start_col] = last_move.piece_moved
        self.board[last_move.end_row][last_move.end_col] = last_move.piece_captured
        self.white_to_move = not self.white_to_move
        if last_move.piece_moved == "wK":
            self.wK_pos = (last_move.start_row, last_move.start_col)
        elif last_move.piece_moved == "bK":
            self.bK_pos = (last_move.start_row, last_move.start_col)
        if last_move.en_passant:
            self.board[last_move.end_row][last_move.end_col] = "--"
            self.board[last_move.start_row][last_move.end_col] = last_move.piece_captured
            self.possible_en_passant = (last_move.start_row, last_move.end_col)
        if last_move.piece_moved[1] == 'P' and abs(last_move.start_row - last_move.end_row) == 2:
            self.possible_en_passant = ()
        if last_move.castle: 
            if last_move.end_col - last_move.start_col == 2: # kingside
                self.board[last_move.end_row][last_move.end_col + 1] = self.board[last_move.end_row][last_move.end_col - 1]
                self.board[last_move.end_row][last_move.end_col - 1] = "--"
            elif last_move.end_col - last_move.start_col == -2: # queenside
                self.board[last_move.end_row][last_move.end_col - 2] = self.board[last_move.end_row][last_move.end_col + 1]
                self.board[last_move.end_row][last_move.end_col + 1] = "--"
        self.checkmate = False
        self.stalemate = False
        self.current_castle_rights_log.pop()
        self.current_castle_rights = self.current_castle_rights_log[-1]
        



    def update_castle_rights(self, move):
        """
        Updates the castle rights of the given gamestate after a move. Does not return anything.
        """
        if move.piece_moved == "wK":
            self.current_castle_rights.wks = False
            self.current_castle_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castle_rights.bks = False
            self.current_castle_rights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7:
                if move.start_col == 7:
                    self.current_castle_rights.wks = False
                elif move.start_col == 0: 
                    self.current_castle_rights.wqs = False
        elif move.piece_moved == "bR":
            if move.start_row == 0:
                if move.start_col == 7:
                    self.current_castle_rights.bks = False
                elif move.start_col == 0: 
                    self.current_castle_rights.bqs = False
        self.current_castle_rights_log.append(self.current_castle_rights)




    def get_valid_moves(self):
        """
        Gets all valid moves on the board with the current state. Considers checks, checkmate, and 
        stalemate. Returns a list of valid moves.
        """
        moves = []
        temp_en_passant = self.possible_en_passant
        self.in_check, self.pins, self.checks = self.find_pins_checks()
        # setting up the current king position
        if self.white_to_move:
            king_pos = self.wK_pos
        else:
            king_pos = self.bK_pos
        if self.in_check: # if in check, the number of moves becomes more limited
            if len(self.checks) == 1: # not a double check (can possibly be blocked)
                moves = self.get_all_moves() # list of moves to edit
                check = self.checks[0] 
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col] # finding the piece that is attacking
                valid_squares = []
                if piece_checking[1] == 'N': # if knight is attacking, it cannot be blocked, must be taken/king must move
                    valid_squares = [(check_row, check_col)]
                else: 
                    for i in range(1, 8): # all squares in direction of check
                        valid_square = (king_pos[0] + check[2] * i, king_pos[1] + check[3] * i) # check[2] and check[3] are the direction coordinates
                        valid_squares.append(valid_square)
                        if (valid_square[0] == check_row and valid_square[1] == check_col): # stop at the piece that is giving check
                            break
                for i in range(len(moves)-1, -1 , -1): # removing elements from move if they are not valid
                    if moves[i].piece_moved[1] != 'K': # making sure the king can move out of the way
                        if not ((moves[i].end_row, moves[i].end_col) in valid_squares):
                            moves.remove(moves[i])
            else: # double check, must move the king
                moves = self.get_king_moves(king_pos[0], king_pos[1], moves)
        else: # no checks, get_all_moves will be OK
            moves = self.get_all_moves()
        if len(moves) == 0: # game has ended
            if self.in_check:
                self.checkmate = True
            else:
                self.stalemate = True
        else: # verifying that checkmate and stalemate are false if there are valid moves
            self.checkmate = False
            self.stalemate = False
        self.possible_en_passant = temp_en_passant
        return moves




    def get_all_moves(self):
        """
        Function to get all moves on the board. Does not consider checks, but does 
        consider pins. Returns a list of all moves.
        """
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[0])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    piece = self.board[r][c][1]
                    if piece == 'P':
                        self.get_pawn_moves(r, c, moves)
                    if piece == 'R':
                        self.get_rook_moves(r, c, moves)
                    if piece == 'N':
                        self.get_knight_moves(r, c, moves)
                    if piece == 'B':
                        self.get_bishop_moves(r, c, moves)
                    if piece == 'Q':
                        self.get_queen_moves(r, c, moves)
                    if piece == 'K':
                        self.get_king_moves(r, c, moves)
        return moves




    def in_bounds(self, r, c):
        """
        Helper function to check if a certain placement (r, c) is within the bounds of the board.
        Returns a boolean value.
        """
        if r < 0 or r > 7:
            return False
        elif c < 0 or c > 7:
            return False
        else:
            return True




    def get_pawn_moves(self, r, c, moves):
        """
        A function to add pawn moves to a given list [moves]. Returns the moves list with the new pawn
        moves added.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        if self.white_to_move:
            king_row, king_col = self.wK_pos
            if self.board[r-1][c] == "--":
                if not piece_pinned or pin_direction == (-1, 0):
                    moves.append(Move((r, c), (r - 1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if self.in_bounds(r-1, c+1):
                if self.board[r-1][c+1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, 1):
                        moves.append(Move((r, c), (r - 1, c + 1), self.board))
                elif (r - 1, c + 1) == self.possible_en_passant:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, is_en_passant=True))
            if self.in_bounds(r-1, c-1):
                if self.board[r-1][c-1][0] == 'b':
                    if not piece_pinned or pin_direction == (-1, -1):
                        moves.append(Move((r, c), (r - 1, c - 1), self.board))
                elif (r - 1, c - 1) == self.possible_en_passant:
                        moves.append(Move((r, c), (r - 1, c - 1), self.board, is_en_passant=True))
        if not self.white_to_move:
            king_row, king_col = self.bK_pos
            if self.board[r+1][c] == "--":
                if not piece_pinned or pin_direction == (1, 0):
                    moves.append(Move((r, c), (r + 1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if self.in_bounds(r+1, c+1):
                if self.board[r+1][c+1][0] == 'w':
                    if not piece_pinned or pin_direction == (1, 1):
                        moves.append(Move((r, c), (r + 1, c + 1), self.board))
                elif (r + 1, c + 1) == self.possible_en_passant:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, is_en_passant=True))
            if self.in_bounds(r+1, c-1):
                if self.board[r+1][c-1][0] == 'w':
                    if not piece_pinned or pin_direction == (1, -1):    
                        moves.append(Move((r, c), (r + 1, c - 1), self.board))
                elif (r + 1, c - 1) == self.possible_en_passant:
                        moves.append(Move((r, c), (r + 1, c - 1), self.board, is_en_passant=True))
        return moves




    def get_rook_moves(self, r, c, moves):
        """
        A function to add possible moves specific for a rook in a given position to a 
        given list [moves]. Returns the updated list of moves.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for d in directions:
            new_r = r + d[0]
            new_c = c + d[1]
            while self.in_bounds(new_r, new_c):
                if not piece_pinned or pin_direction == (d[0], d[1]) or pin_direction == (-d[0], -d[1]):
                    if self.board[new_r][new_c] == "--":
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                    turn = self.board[new_r][new_c][0]
                    if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                        break
                    elif (turn == 'w' and not self.white_to_move) or (turn == 'b' and self.white_to_move):
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    new_r += d[0]
                    new_c += d[1]
                else:
                    break
        return moves




    def get_knight_moves(self, r, c, moves):
        """
        A function to add possible moves specific for a knight in a given position to a 
        given list [moves]. Returns the updated list of moves.
        """
        piece_pinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])
                break
        directions = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))
        for d in directions:
            new_r = r + d[0]
            new_c = c + d[1]
            if self.in_bounds(new_r, new_c):
                if piece_pinned:
                    return moves
                else:
                    if self.board[new_r][new_c][0] != ('w' if self.white_to_move else 'b'):
                        moves.append(Move((r, c), (new_r, new_c), self.board))
        return moves




    def get_bishop_moves(self, r, c, moves):
        """
        A function to add possible moves specific for a bishop in a given position to a 
        given list [moves]. Returns the updated list of moves.
        """
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = ((1, 1), (1, -1), (-1, 1), (-1, -1))
        for d in directions:
            new_r = r + d[0]
            new_c = c + d[1]
            while self.in_bounds(new_r, new_c):
                if not piece_pinned or pin_direction == (d[0], d[1]) or pin_direction == (-d[0], -d[1]):
                    if self.board[new_r][new_c] == "--":
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                    turn = self.board[new_r][new_c][0]
                    if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                        break
                    elif (turn == 'w' and not self.white_to_move) or (turn == 'b' and self.white_to_move):
                        moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    new_r += d[0]
                    new_c += d[1]
                else: 
                    break
        return moves




    def get_queen_moves(self, r, c, moves):
        """
        A function to add possible queen moves in a given position. It is a combination of 
        the get_rook_moves and get_bishop_moves. Returns the updated moves list.
        """
        moves = self.get_rook_moves(r, c, moves)
        moves = self.get_bishop_moves(r, c, moves)
        return moves




    def get_king_moves(self, r, c, moves):
        """
        A function to add possible king moves in a given position. 
        """
        directions = ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1))
        if self.white_to_move:
            ally = 'w'
        else:
            ally = 'b'
        for d in directions:
            new_r = r + d[0]
            new_c = c + d[1]
            if self.in_bounds(new_r, new_c):
                if self.white_to_move and self.board[new_r][new_c][0] != ally:
                    self.wK_pos = (new_r, new_c)
                elif not self.white_to_move and self.board[new_r][new_c][0] != ally:
                    self.bK_pos = (new_r, new_c)
                in_check, pins, checks = self.find_pins_checks()
                if not in_check and self.board[new_r][new_c][0] != ally:
                    moves.append(Move((r, c), (new_r, new_c), self.board))
                    if self.white_to_move:
                        self.wK_pos = (r, c)
                    else:
                        self.bK_pos = (r, c)
                else:
                    if self.white_to_move:
                        self.wK_pos = (r, c)
                    else:
                        self.bK_pos = (r, c)
        moves = self.get_castle_moves(r, c, moves, ally)
        return moves
    



    def get_castle_moves(self, r, c, moves, ally):
        """
        Gets all castle moves available to the current king
        """
        in_check, pins, checks = self.find_pins_checks()
        if in_check:
            return
        else:
            if (self.white_to_move and self.current_castle_rights.wks == True) or (not self.white_to_move and self.current_castle_rights.bks == True):
                moves = self.get_kingside(r, c, moves, checks, ally)
            if (self.white_to_move and self.current_castle_rights.wqs == True) or (not self.white_to_move and self.current_castle_rights.bqs == True):
                moves = self.get_queenside(r, c, moves, checks, ally)
        return moves




    def get_kingside(self, r, c, moves, checks, ally):
        """
        Gets kingside castle moves for both black and white. Returns the updated moves list
        """
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            add = True
            for check in checks:
                if (r == check[0] and c+1 == check[1]) or (r == check[0] and c+2 == check[1]):
                    add = False
            if add:
                if self.current_castle_rights.wks and ally == 'w':
                    self.wK_pos = (r, c+2)
                    in_check, pins, checks = self.find_pins_checks()
                    if not in_check:
                        moves.append(Move((r, c), (r, c+2), self.board, is_castle_move=True))
                    self.wK_pos = (r, c)
                if self.current_castle_rights.bks and ally == 'b': 
                    self.bK_pos = (r, c+2)
                    in_check, pins, checks = self.find_pins_checks()
                    if not in_check:
                        moves.append(Move((r, c), (r, c+2), self.board, is_castle_move=True))
                    self.bK_pos = (r, c)       
        return moves




    def get_queenside(self, r, c, moves, checks, ally):
        """
        Gets queenside castle moves for both black and white. Returns the updated moves list
        """
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3]:
            add = True
            for check in checks:
                if (r == check[0] and c-1 == check[1]) or (r == check[0] and c-2 == check[1]):
                    add = False
            if add:
                if self.current_castle_rights.wqs and ally == 'w':
                    self.wK_pos = (r, c-2)
                    in_check, pins, checks = self.find_pins_checks()
                    if not in_check:
                        moves.append(Move((r, c), (r, c-2), self.board, is_castle_move=True))
                    self.wK_pos = (r, c)
                if self.current_castle_rights.bqs and ally == 'b': 
                    self.bK_pos = (r, c-2)
                    in_check, pins, checks = self.find_pins_checks()
                    if not in_check:
                        moves.append(Move((r, c), (r, c-2), self.board, is_castle_move=True))
                    self.bK_pos = (r, c)
        return moves




    def find_pins_checks(self):
        pins = []
        checks = []
        in_check = False
        if self.white_to_move:
            enemy = 'b'
            ally = 'w'
            start_row = self.wK_pos[0]
            start_col = self.wK_pos[1]
        else:
            enemy = 'w'
            ally = 'b'
            start_row = self.bK_pos[0]
            start_col = self.bK_pos[1]
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)) # outward directions
        for i in range(len(directions)):
            d = directions[i]
            possible_pin = () # position of piece which may be pinned
            for j in range(1, 8):
                end_row = start_row + d[0] * j
                end_col = start_col + d[1] * j
                if self.in_bounds(end_row, end_col):
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally and end_piece[1] != 'K':
                        if possible_pin == (): # first ally piece, could be a pin
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else: # second ally piece, we can break (not a pin)
                            break
                    elif end_piece[0] == enemy:
                        type = end_piece[1]
                        if (0 <= i <= 3 and type == 'R') or \
                            (4 <= i <= 7 and type == 'B') or \
                            (j == 1 and type == 'P' and ((enemy == 'w' and 6 <= i <= 7) or (enemy == 'b' and 4 <= i <= 5))) or \
                            (type == 'Q') or (j == 1 and type == 'K'):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:
                                pins.append(possible_pin)
                                break
                        else: 
                            break
                else: 
                    break
        knight_moves = ((2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))
        for d in knight_moves:
            end_row = start_row + d[0]
            end_col = start_col + d[1]
            if self.in_bounds(end_row, end_col):
                piece = self.board[end_row][end_col]
                if piece[0] == enemy and piece[1] == 'N':
                    in_check = True
                    checks.append((end_row, end_col, d[0], d[1]))
        return in_check, pins, checks


"""
A tracker to see if we are allowed to castle at any given moment
"""
class CastleRights:

    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:

    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4,
                     "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3,
                     "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}



    def __init__(self, start, end, board, is_en_passant=False, is_castle_move=False):
        self.start_row = start[0]
        self.start_col = start[1]
        self.end_row = end[0]
        self.end_col = end[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        # pawn promotion
        self.pawn_promotion = (self.piece_moved == "wP" and self.end_row == 0) or (self.piece_moved == "bP" and self.end_row == 7)
        # en passant
        self.en_passant = is_en_passant
        # castle
        self.castle = is_castle_move

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col





    def __eq__(self, other):
        """
        Overriding the equals method
        """
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False




    def __str__(self):
        return f"({self.start_row}, {self.start_col}), ({self.end_row}, {self.end_col}). Piece moved: {self.piece_moved}"




    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + "->" + self.get_rank_file(self.end_row, self.end_col)




    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
