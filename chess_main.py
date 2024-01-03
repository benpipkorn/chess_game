import pygame as p
import chess_engine
import so_smart as ai

RATIO = 3 / 2 # the width to height ratio of the screen
HEIGHT = 500
WIDTH = HEIGHT * RATIO # 5:4 ratio for width to height, for move log/game updates
FONT_SIZE = HEIGHT // 40
DIMENSION = 8
SQ_DIM = HEIGHT // DIMENSION
MAX_FPS = 60
IMAGES = {}

def load_images():
    pieces = ["bB", "bK", "bN", "bP", "bQ", "bR", "wB", "wK", "wN", "wP", "wQ", "wR",]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_DIM * 0.85, SQ_DIM * 0.85))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = chess_engine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False # tracking if we have made a move or not
    animate = False # tracking if we need to animate a move or not
    line_count = 1
    load_images()
    sq_selected = ()
    clicks = []
    running = True
    game_over = False
    player_one = True # If true, human will play as white
    player_two = True # If true, human will play as black
    while running: 
        human_move = (gs.white_to_move and player_one) or (not gs.white_to_move and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN: # registering clicks
                if not game_over and human_move:
                    location = p.mouse.get_pos() # first position, assigning values to row and column on board
                    row = location[1] // SQ_DIM
                    col = location[0] // SQ_DIM
                    if sq_selected == (row, col): # ensures a new square is selected before anything is added
                        sq_selected = ()
                        clicks = []                    
                    else: # adding new click location to clicks list
                        sq_selected = (row, col)
                        clicks.append(sq_selected)
                    if len(clicks) == 2: # a new move has been made
                        next_move = chess_engine.Move(clicks[0], clicks[1], gs.board) # creating a Move object with the  given clicks
                        for i in range(len(valid_moves)): 
                            if next_move == valid_moves[i]: # ensuring the move made is a valid move
                                text = next_move.get_chess_notation()
                                draw_text(screen, gs, line_count, text) # updating the move log shown on the right side of the screen
                                if line_count + (FONT_SIZE * RATIO) + (FONT_SIZE * 2) < HEIGHT: # moving the next line down if there is room
                                    line_count += 1 
                                gs.make_move(valid_moves[i]) # making the move and setting flags
                                move_made = True
                                animate = True
                                sq_selected = () # resetting click values if the move was valid
                                clicks = []
                        if not move_made: # resetting the clicks if a move was not valid so that the same square is selected
                            clicks = [sq_selected]
            elif e.type == p.KEYDOWN: # registering keyboard clicks
                key_pressed = p.key.get_pressed()
                if key_pressed[p.K_u]: # [U] key, undo a move
                    if gs.move_log == []: # empty move log
                        draw_text(screen, gs, line_count, "No moves made.")
                        break
                    gs.undo_move() # setting move_made flag as true, not animate though (looks funky)
                    if player_one ^ player_two: # undoing move made by ai as well if one human is playing
                        gs.undo_move()
                        line_count -= 1
                    line_count -= 1 # line count goes down since it is an undo, and since a move has been removed from the move log
                    move_made = True
                    draw_text(screen, gs, line_count, "Move undone.")
                    sq_selected = () # resetting clicks
                    clicks = []
                    game_over = False # in case of checkmate / stalemate
                if key_pressed[p.K_r]: # [R] clicked, resetting game
                    line_count = 1 # line count starts at beginning again
                    draw_text(screen, gs, line_count, "New game.")
                    gs = chess_engine.GameState() # new GameState object with fresh flags and properties
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    clicks = []
                    move_made = False
                    animate = False
                    game_over = False
        # AI move finder
        if not game_over and not human_move:
            next_move = ai.find_best_move(gs, valid_moves)
            if next_move == None:
                next_move = ai.find_random_move(valid_moves)
            text = next_move.get_chess_notation()
            draw_text(screen, gs, line_count, text) # updating the move log shown on the right side of the screen
            if line_count + (FONT_SIZE * RATIO) + (FONT_SIZE * 2) < HEIGHT: # moving the next line down if there is room
                line_count += 1 
            gs.make_move(next_move) # making the move and setting flags
            move_made = True
            animate = True
        if move_made: # move has been made or undone
            move_made = False 
            if animate: # animating a move
                animate_piece(next_move, screen, gs.board, clock)
                animate = False
            valid_moves = gs.get_valid_moves() # new set of valid moves
        if gs.checkmate or gs.stalemate: # displaying a prompt to get out of checkmate / stalemate
            if gs.white_to_move:
                turn = "black"
            else:
                turn = "white"
            draw_text(screen, gs, line_count, f"Checkmate, {turn} wins. Please press [R] to restart or [U] to undo.")
            game_over = True # game is over
            gs.checkmate = False #setting these to false so it does not constantly run
            gs.stalemate = False
        draw_game_state(screen, gs, valid_moves, sq_selected) # draw GameState after everything has been changed
        clock.tick(MAX_FPS)
        p.display.flip()

def draw_text(screen, gs, line_count, text, style="cherry", bold=False):
    text_surface = p.Surface((WIDTH * (RATIO - 1), HEIGHT)) # portion of the screen not on the board
    text_surface.fill(p.Color("white"))
    font = p.font.Font("fonts/" + style + ".ttf", FONT_SIZE)
    j = 1 # iterator for the history_location
    for i in range(-1, -(line_count), -1): # for loop to print a move log. newest appears on top. starts on second line
        history_obj = font.render(gs.move_log[i].get_chess_notation(), True, p.Color("black"))
        history_location = p.Rect(0, (FONT_SIZE * RATIO * j), WIDTH * (RATIO - 1), FONT_SIZE + (FONT_SIZE * RATIO))
        text_surface.blit(history_obj, history_location)
        j += 1
    text_obj = font.render(text, True, p.Color("black")) # final information displayed in the log (could be move notation, move undone, or game over update)
    text_location = p.Rect(0, 0, WIDTH * (RATIO - 1), FONT_SIZE + (FONT_SIZE * RATIO))
    text_surface.blit(text_obj, text_location)
    screen.blit(text_surface, (HEIGHT, 0))

def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != (): # one square selected
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'): # checking it was a valid piece to select
            center_highlight = SQ_DIM*0.05 # setting up highlights
            s = p.Surface((SQ_DIM * 0.90, SQ_DIM * 0.90)) 
            s.set_alpha(80) # transparency value (0 - 255)
            s.fill(p.Color("yellow"))
            screen.blit(s, (c * SQ_DIM + center_highlight, r * SQ_DIM + center_highlight)) # highlighting square of piece selected
            s.fill(p.Color("grey"))
            for move in valid_moves: # hightlighting all valid moves for the piece selected
                if move.start_row == r and move.start_col == c:
                    end_r = move.end_row
                    end_c = move.end_col
                    screen.blit(s, (end_c * SQ_DIM + center_highlight, end_r * SQ_DIM + center_highlight))

def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen, gs.move_log)
    highlight_squares(screen, gs, valid_moves, sq_selected) # doing this before pieces so pieces are not highlighted
    draw_pieces(screen, gs.board)

def draw_board(screen, move_log=[]):
    global colors
    colors = [p.Color("darkseagreen2"), p.Color("darkseagreen3")] # light, dark, highlighted
    for x in range(DIMENSION): # drawing pattern
        for y in range(DIMENSION):
            p.draw.rect(screen, colors[(x + y) % 2], p.Rect((x * SQ_DIM, y * SQ_DIM), (SQ_DIM, SQ_DIM)))
    s = p.Surface((SQ_DIM, SQ_DIM))
    s.set_alpha(80)
    s.fill(p.Color("yellow"))
    if move_log != []: # highlighting last move made
        screen.blit(s, (move_log[-1].end_col * SQ_DIM, move_log[-1].end_row * SQ_DIM))
        s.set_alpha(40)
        screen.blit(s, (move_log[-1].start_col * SQ_DIM, move_log[-1].start_row * SQ_DIM))

def draw_pieces(screen, board):
    global center_piece
    center_piece = SQ_DIM*0.075
    for x in range(DIMENSION): # drawing all pieces on correct squares
        for y in range(DIMENSION):
            piece = board[y][x]
            if piece != "--":
                screen.blit(IMAGES[piece], (x * SQ_DIM + center_piece, y * SQ_DIM + center_piece))

def animate_piece(move, screen, board, clock):
    global colors
    global center_piece
    d_r = move.end_row - move.start_row # change in row and change in col
    d_c = move.end_col - move.start_col
    frames_per_sq = 10
    frame_count = (abs(d_r) + abs(d_c)) * frames_per_sq # total frames to be drawn
    for frame in range(frame_count + 1): # drawing board for all frames
        r, c = (move.start_row + (d_r * frame / frame_count), move.start_col + (d_c * frame / frame_count)) # iteration frame location for piece image
        draw_board(screen)
        draw_pieces(screen, board)
        # erasing piece moved from end square until it gets there
        color = colors[(move.end_row + move.end_col) % 2]
        end_sq = p.Rect(move.end_col * SQ_DIM, move.end_row * SQ_DIM, SQ_DIM, SQ_DIM)
        p.draw.rect(screen, color, end_sq)
        # redrawing piece captured in end square
        if move.piece_captured != "--":
            screen.blit(IMAGES[move.piece_captured], (move.end_col * SQ_DIM + center_piece, move.end_row * SQ_DIM + center_piece))
        screen.blit(IMAGES[move.piece_moved], (c * SQ_DIM + center_piece, r * SQ_DIM + center_piece))
        p.display.flip()
        clock.tick(120)


if __name__ == "__main__":
    main()