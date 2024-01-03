import random
import chess_engine


piece_vals = {"K": 0, "Q": 9, "R": 5, "B": 3, "N": 3, "P": 1}

king_eval = [[3, 3, 3, 1, 1, 3, 3, 3],
             [3, 2, 1, 0, 0, 1, 2, 3],
             [1, 1, 0, 0, 0, 0, 1, 1],
             [1, 0, 0, 0, 0, 0, 0, 1],
             [1, 0, 0, 0, 0, 0, 0, 1],
             [1, 1, 0, 0, 0, 0, 1, 1],
             [3, 2, 1, 0, 0, 1, 2, 3],
             [3, 3, 3, 1, 1, 3, 3, 3]]

queen_eval = [[1, 2, 3, 3, 3, 3, 2, 1],
              [2, 3, 3, 4, 4, 3, 2, 2],
              [3, 3, 4, 4, 4, 4, 3, 3],
              [3, 3, 4, 5, 5, 4, 3, 3],
              [3, 3, 4, 5, 5, 4, 3, 3],
              [3, 3, 4, 4, 4, 4, 3, 3],
              [2, 3, 3, 4, 4, 3, 2, 2],
              [1, 2, 3, 3, 3, 3, 2, 1]]

rook_eval = [[1, 1, 1, 1, 1, 1, 1, 1],
             [2, 2, 2, 2, 2, 2, 2, 2],
             [2, 2, 3, 3, 3, 3, 2, 2],
             [2, 2, 3, 4, 4, 3, 2, 2],
             [2, 2, 3, 4, 4, 3, 2, 2],
             [2, 2, 3, 3, 3, 3, 2, 2],
             [2, 2, 2, 2, 2, 2, 2, 2],
             [1, 1, 1, 1, 1, 1, 1, 1]]

bishop_eval = [[2, 1, 2, 2, 2, 2, 1, 2],
               [1, 3, 2, 3, 3, 2, 3, 1],
               [1, 2, 4, 3, 3, 4, 2, 1],
               [1, 2, 3, 5, 5, 3, 2, 1],
               [1, 2, 3, 5, 5, 3, 2, 1],
               [1, 2, 4, 3, 3, 4, 2, 1],
               [1, 3, 2, 3, 3, 2, 3, 1],
               [2, 1, 2, 2, 2, 2, 1, 2]]

knight_eval = [[1, 1, 1, 1, 1, 1, 1, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 3, 3, 3, 2, 1],
               [1, 2, 2, 2, 2, 2, 2, 1],
               [1, 1, 1, 1, 1, 1, 1, 1]]

pawn_eval = [[0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],
             [0, 0, 0, 0, 0, 0, 0, 0],]

piece_evals = {"K": king_eval, "Q": queen_eval, "R": rook_eval, "B": bishop_eval, "N": knight_eval, "P": pawn_eval}

CHECKMATE = 1_000_000
STALEMATE = 0
MAX_DEPTH = 4
# positive score means white is winning, negative score means black is winning

def find_random_move(valid_moves):
    """
    Finds a random move for a given list or random moves
    """
    return valid_moves[random.randint(0, len(valid_moves) - 1)]


def find_best_move(gs, valid_moves):
    global next_move
    next_move = None
    random.shuffle(valid_moves)
    #minimax(gs, valid_moves, MAX_DEPTH, True if gs.white_to_move else False)
    negamax_alpha_beta(gs, valid_moves, MAX_DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.white_to_move else -1)
    return next_move


def best_move(gs, valid_moves):
    """
    A way to find the next best move for an AI. Searches through all possible moves and 
    evaluates what to do next based on a min max function.
    """
    sign = 1 if gs.white_to_move else -1
    max_score = -CHECKMATE # lowest value it can be right now
    best_move = None
    for move in valid_moves:
        move = find_random_move(valid_moves) # finding random move temporarily so moves are not repeated between AI
        gs.make_move(move)
        if gs.checkmate:
            score = CHECKMATE
        elif gs.stalemate:
            score = STALEMATE
        else:
            score = score_board(gs.board) * sign
        if (score > max_score): # evaluating score and finding the max score
            best_move = move
            max_score = score
        gs.undo_move()
    return best_move, max_score



def score_board(gs):
    """
    A way to evaluate a certain position on a board.
    """
    if gs.checkmate:
        if gs.white_to_move:
            return -CHECKMATE
        else:
            return CHECKMATE
    if gs.stalemate:
        return STALEMATE
    
    score = 0 
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != "--":
                pos_eval = piece_evals[square[1]]
                piece_total = piece_vals[square[1]] + pos_eval[row][col]
                if square[0] == "w":
                    score += piece_total
                elif square[0] == "b":
                    score -= piece_total
    return score





def minimax(gs, valid_moves, depth, white_to_move):
    """
    A min max algorithm to find the best set of moves to play given a certain depth by 
    evaluating various positions and trying to get the largest. The deeper the depth, 
    the better the AI will be, and the longer it will take to move.
    """
    global next_move
    if depth == 0:
        return score_board(gs)
    if white_to_move:  
        max_score = -CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            new_valid_moves = gs.get_valid_moves()
            score = minimax(gs, new_valid_moves, depth - 1, False)
            if score > max_score:
                max_score = score
                if depth == MAX_DEPTH:
                    next_move = move
            gs.undo_move()
        return max_score
    else: 
        min_score = CHECKMATE
        for move in valid_moves:
            gs.make_move(move)
            new_valid_moves = gs.get_valid_moves()
            score = minimax(gs, new_valid_moves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == MAX_DEPTH:
                    next_move = move
            gs.undo_move()
        return min_score

def negamax(gs, valid_moves, depth, sign):
    """
    A negamax algorithm to find the best set of moves to play given a certain depth by 
    evaluating various positions and trying to get the largest. The deeper the depth, 
    the better the AI will be, and the longer it will take to move. The sign determines 
    which value we will be adding to
    """
    global next_move
    if depth == 0: # base case
        return score_board(gs) * sign
    
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        new_valid_moves = gs.get_valid_moves()
        score = -negamax(gs, new_valid_moves, depth - 1, -sign)
        if score > max_score:
            max_score = score
            if depth == MAX_DEPTH:
                next_move = move
        gs.undo_move()
    return max_score

def negamax_alpha_beta(gs, valid_moves, depth, alpha, beta, sign):
    """
    A negamax algorithm to find the best set of moves to play given a certain depth by 
    evaluating various positions and trying to get the largest. The deeper the depth, 
    the better the AI will be, and the longer it will take to move. The sign determines 
    which value we will be adding to
    """
    global next_move
    if depth == 0: # base case
        return score_board(gs) * sign
    
    max_score = -CHECKMATE
    for move in valid_moves:
        gs.make_move(move)
        new_valid_moves = gs.get_valid_moves()
        score = -negamax_alpha_beta(gs, new_valid_moves, depth - 1, -beta, -alpha, -sign)
        if score > max_score:
            max_score = score
            if depth == MAX_DEPTH:
                next_move = move
        gs.undo_move()
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break
    return max_score