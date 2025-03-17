# -*- coding: utf-8 -*-
import curses
import time
import random

def main(stdscr):
    # Initialize curses
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(True)
    curses.curs_set(0)
    score = 0
    high_score = 0
    reloadSpeed = 0.2
    movement = 5
    start_time = time.time()
    
    # Get screen size
    screen_height, screen_width = stdscr.getmaxyx()
    
    # Set up player position
    player_x = (screen_width // 2 - 8) // 5 * 5
    space = 30  # Default width of the landing strip

    # Game loop settings
    stdscr.nodelay(False)  # Wait for user input on menus
    stdscr.timeout(100)  # Control game speed

    ascii_art = [
        r"·························································",
        r": ______    __   __  __    _  _     _  _______  __   __ :",
        r":|    _ |  |  | |  ||  |  | || | _ | ||   _   ||  | |  |:",
        r":|   | ||  |  | |  ||   |_| || || || ||  |_|  ||  |_|  |:",
        r":|   |_||_ |  |_|  ||       ||       ||       ||       |:",
        r":|    __  ||       ||  _    ||       ||       ||_     _|:",
        r":|   |  | ||       || | |   ||   _   ||   _   |  |   |  :",
        r":|___|  |_||_______||_|  |__||__| |__||__| |__|  |___|  :",
        r":         ______    __   __  _______  __   __           :",
        r":        |    _ |  |  | |  ||       ||  | |  |          :",
        r":        |   | ||  |  | |  ||  _____||  |_|  |          :",
        r":        |   |_||_ |  |_|  || |_____ |       |          :",
        r":        |    __  ||       ||_____  ||       |          :",
        r":        |   |  | ||       | _____| ||   _   |          :",
        r":        |___|  |_||_______||_______||__| |__|          :",
        r"·························································"
    ]

    def draw_player(win, x):
        """ Draw the player (plane) at the given x-coordinate. """
        player = [
            r"       _ ",       
            r"      /*\ ",      
            r"     /***\ ",     
            r"  __/-----\__ ",  
            r" /  |     |  \ ", 
            r"/___|_____|___\ ",
            r"    \  ||  / ",
            r"     \_||_/ "    
        ]
        for i, line in enumerate(player):
            win.addstr(screen_height - 10 + i, x, line)

    def draw_strip(win, strip_x, strip_y, space):
        """ Draw the landing strip at given position. """
        max_y, max_x = win.getmaxyx()
        for i in range(5):  # Assuming 5 lines for the strip
            if strip_y + i < max_y and strip_x + 11 + space < max_x:  # Ensure within bounds
                win.addstr(strip_y + i, strip_x, "|||||" + " " * space + "|||||")
            else:
                break  # Stop drawing if out of bounds

    def show_message(win, message):
        """ Display a message in the center of the screen. """
        win.clear()
        win.addstr(screen_height // 2, screen_width // 2 - len(message) // 2, message)
        win.refresh()

    def show_ascii_art(win):
        """ Display ASCII art at the top of the screen. """
        win.clear()
        y = screen_height // 2 - 10
        for line in ascii_art:
            win.addstr(y, screen_width // 2 - 27, line)
            y += 1
        win.refresh()
        time.sleep(2)  # Show for 2 seconds

    def show_instructions(win):
        """ Display instructions screen. """
        win.clear()
        instructions = [
            "***********************************************************************",
            "*                           Instructions:                             *",
            "* 1. Use the LEFT and RIGHT arrow keys to move the player             *",
            "* 2. Your goal is to land the plane on the airstrip without crashing  *",
            "* 3. As the game progresses, the levels will get harder and faster    *",
            "* 4. Press the ESC key to exit at any time                            *",
            "*                                                                     *",
            "*                    Press ENTER to start the game                    *",
            "***********************************************************************"
        ]
        for i, line in enumerate(instructions):
            win.addstr(screen_height // 2 - 4 + i, screen_width // 2 - len(line) // 2, line)
        win.refresh()

    def show_score(win, score, high_score, elapsed_time):
        """ Display the score, high score, and elapsed time at the top of the screen. """
        win.addstr(0, 0, "Score: {}".format(str(score).zfill(3)))
        win.addstr(1, 0, "High Score: {}".format(str(high_score).zfill(3)))
        win.addstr(2, 0, "Time: {:.1f}s".format(elapsed_time))
        win.refresh()

    # Show ASCII art first
    show_ascii_art(stdscr)

    # Show start message
    show_message(stdscr, "Press ENTER to Start or ESC to Exit")
    while True:
        key = stdscr.getch()
        if key == 27:  # ESC key
            return
        if key == 10:  # ENTER key
            break

    # Show instructions
    show_instructions(stdscr)
    while True:
        key = stdscr.getch()
        if key == 27:  # ESC key
            return
        if key == 10:  # ENTER key
            break

    # Game loop
    strip_x = random.randint(1, (screen_width - space - 15) // 5) * 5  # Initial strip position
    strip_y = 5  # Initial strip position
    stdscr.nodelay(True)  # Enable continuous movement

    while True:
        stdscr.clear()

        # Move the landing strip downward
        strip_y += 1
        if strip_y >= screen_height - 10:
            if player_x < strip_x or player_x > strip_x + space:
                show_message(stdscr, "You crashed! Press ENTER to restart or ESC to exit -- Score: {}".format(score))
                while True:
                    key = stdscr.getch()
                    if key == 27:  # ESC key
                        show_message(stdscr, "High Score: {}!!!".format(high_score))
                        stdscr.refresh()
                        time.sleep(2)
                        exit() 
                        
                    if key == 10:
                        stdscr.clear()
                        stdscr.refresh()
                        strip_y = 5
                        strip_x = random.randint(1, (screen_width - space - 15) // 5) * 5
                        movement += 1
                        space = random.randint(20, 40)
                        start_time = time.time()
                        reloadSpeed = 0.2
                        movement = 5
                        break
                    
                score = 0  # Reset score after crash
                reloadSpeed = 0.2
                movement = 5
            elif player_x >= strip_x and player_x <= strip_x + space:
                score += 1
                reloadSpeed = min (0.1, reloadSpeed - 0.01)
                strip_y = 5
                strip_x = random.randint(1, (screen_width - space - 15) // 5) * 5
                movement += 1
                space = random.randint(20, 40)
                if score > high_score:
                    high_score = score  # Update high score

        key = stdscr.getch()
        if key == curses.KEY_LEFT:
            player_x = max(5, player_x - movement)  # Move left
        elif key == curses.KEY_RIGHT:
            player_x = min(screen_width - 20, player_x + movement)  # Move right
        elif key == 27 or key == ord('q'):  # ESC or 'q' key to quit
            break

        # Draw everything
        draw_strip(stdscr, strip_x, strip_y, space)
        draw_player(stdscr, player_x)
        elapsed_time = time.time() - start_time
        show_score(stdscr, score, high_score, elapsed_time)

        stdscr.refresh()
        time.sleep(reloadSpeed)  # Control game speed

    # Cleanup and exit
    curses.nocbreak()
    stdscr.keypad(False)
    curses.echo()
    curses.endwin()

# Run the game
curses.wrapper(main)