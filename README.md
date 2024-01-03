# Chess Game
A chess bot built using Python and Pygame

## Summary
This implementation can be played in a two-player mode, or one-player against a bot. The bot uses a minimax algorithm with alpha-beta pruning to calculate the best moves to play.

## How to use
To run this, run the 'chess_main.py' file. The current setting is two-player mode. To change this, you can set the variable 'player_one' to 'False' to have the bot play as white. If you would like to play as white, set the variable 'player_two' to 'False'. These variables can be found in the main file around line 30.
You may change the color of the board if you like as well. This can be done by choosing any valid Pygame color ([link to names of valid colors](https://www.pygame.org/docs/ref/color_list.html)). To change the colors, visit the function 'draw_board' in the main file and edit the names of the global list 'colors'. 
