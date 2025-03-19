import curses
import time
import random
import threading

def init_screen():
    stdscr = curses.initscr()
    curses.curs_set(0)  # Hide the cursor
    stdscr.keypad(True)  # Enable keypad mode for arrow keys
    curses.noecho()  # Don't echo input
    curses.cbreak()  # React to keys instantly

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()  # Ensure default background
        curses.init_pair(1, curses.COLOR_RED, -1)      # Bricks
        curses.init_pair(2, curses.COLOR_GREEN, -1)    # Paddle
        curses.init_pair(3, curses.COLOR_YELLOW, -1)   # Ball
        curses.init_pair(4, curses.COLOR_CYAN, -1)     # Pause Message

    return stdscr

def draw_game(game_win, game_state):
    game_win.clear()
    game_win.border(0)

    height, width = game_win.getmaxyx()

    # Draw bricks
    game_win.attron(curses.color_pair(1))
    for y, x in game_state["bricks"]:
        if 0 <= y < height and 0 <= x < width:
            for i in range(4):  # 4-wide bricks
                if x + i < width:
                    game_win.addch(y, x + i, "#")
    game_win.attroff(curses.color_pair(1))

    # Draw paddle
    game_win.attron(curses.color_pair(2))
    paddle_y = height - 2
    for i in range(15):  # Increased paddle size to make it easier
        paddle_x = game_state["paddle_x"] + i
        if 0 <= paddle_x < width - 1:
            game_win.addch(paddle_y, paddle_x, "=")
    game_win.attroff(curses.color_pair(2))

    # Draw ball (2x2 block)
    game_win.attron(curses.color_pair(3))
    ball_y, ball_x = int(game_state["ball_y"]), int(game_state["ball_x"])  # Convert to integers
    if 0 <= ball_y < height - 1 and 0 <= ball_x < width - 1:
        game_win.addstr(ball_y, ball_x, "*")
        game_win.addstr(ball_y, ball_x + 1, "*")
        game_win.addstr(ball_y + 1, ball_x, "*")
        game_win.addstr(ball_y + 1, ball_x + 1, "*")
    game_win.attroff(curses.color_pair(3))

    # Display score and lives
    game_win.addstr(0, 2, f"Score: {game_state['score']}  Lives: {game_state['lives']}")

    # Display pause message
    if game_state["paused"]:
        game_win.attron(curses.color_pair(4))
        game_win.addstr(height // 2, width // 2 - 3, "Paused")
        game_win.attroff(curses.color_pair(4))

    game_win.refresh()

def move_ball(game_win, game_state, height, width, pause_event):
    while not game_state["game_over"]:
        if not game_state["paused"]:
            # Store previous position for better collision detection
            prev_y = game_state["ball_y"]
            prev_x = game_state["ball_x"]
            
            # Update ball position
            game_state["ball_y"] += game_state["ball_dir_y"]
            game_state["ball_x"] += game_state["ball_dir_x"]

            # Ball collision with walls
            if game_state["ball_x"] <= 1:
                game_state["ball_x"] = 2
                game_state["ball_dir_x"] *= -1
            elif game_state["ball_x"] >= width - 3:  # Adjusted for ball width
                game_state["ball_x"] = width - 3
                game_state["ball_dir_x"] *= -1

            if game_state["ball_y"] <= 1:
                game_state["ball_y"] = 2
                game_state["ball_dir_y"] *= -1

            # Improved paddle collision detection
            paddle_top = height - 3
            paddle_left = game_state["paddle_x"]
            paddle_right = game_state["paddle_x"] + 15

            # Check if ball is at paddle height and moving downward
            if (game_state["ball_y"] >= paddle_top - 1 and prev_y < paddle_top - 1 and 
                game_state["ball_dir_y"] > 0):  # Only check when ball is moving down
                # Check if ball overlaps with paddle (accounting for 2x2 ball size)
                if paddle_left - 1 <= game_state["ball_x"] <= paddle_right:
                    game_state["ball_y"] = paddle_top - 2  # Place ball just above paddle
                    game_state["ball_dir_y"] *= -1  # Reverse vertical direction
                    
                    # Calculate hit position relative to paddle center for angle
                    paddle_center = paddle_left + 7.5
                    hit_position = game_state["ball_x"] - paddle_left
                    
                    # Adjust ball direction based on where it hits the paddle
                    if hit_position < 3:  # Left edge
                        game_state["ball_dir_x"] = -1.5
                    elif hit_position < 6:  # Left middle
                        game_state["ball_dir_x"] = -1.0
                    elif hit_position < 9:  # Center
                        game_state["ball_dir_x"] = 0
                    elif hit_position < 12:  # Right middle
                        game_state["ball_dir_x"] = 1.0
                    else:  # Right edge
                        game_state["ball_dir_x"] = 1.5

            # Ball collision with bricks - proactive detection
            new_bricks = []
            ball_hit_brick = False
            
            # Get next ball position (one step ahead)
            next_ball_y = int(game_state["ball_y"] + game_state["ball_dir_y"])
            next_ball_x = int(game_state["ball_x"] + game_state["ball_dir_x"])
            
            # Get ball boundaries for next position (accounting for 2x2 size)
            ball_left = next_ball_x
            ball_right = next_ball_x + 1
            ball_top = next_ball_y
            ball_bottom = next_ball_y + 1

            for y, x in game_state["bricks"]:
                # Brick boundaries
                brick_left = x
                brick_right = x + 3  # 4-wide brick
                brick_top = y
                brick_bottom = y

                # Check for any overlap between next ball position and brick
                if not (ball_right < brick_left or     # ball is left of brick
                        ball_left > brick_right or     # ball is right of brick
                        ball_bottom < brick_top or     # ball is above brick
                        ball_top > brick_bottom):      # ball is below brick
                    if not ball_hit_brick:
                        game_state["ball_dir_y"] *= -1
                        ball_hit_brick = True
                    game_state["score"] += 10
                else:
                    new_bricks.append((y, x))
            
            game_state["bricks"] = new_bricks

            # Ball falls below paddle - improved detection
            if int(game_state["ball_y"]) >= height - 2:  # Check both rows of the 2x2 ball
                game_state["lives"] -= 1
                if game_state["lives"] <= 0:
                    game_state["game_over"] = True
                else:
                    # Reset ball position
                    game_state["ball_y"] = height - 4
                    game_state["ball_x"] = width // 2
                    game_state["ball_dir_y"] = -1
                    game_state["ball_dir_x"] = random.choice([-1, -0.5, 0.5, 1])
                    game_state["paddle_x"] = width // 2 - 7  # Reset paddle position too

            # Check win condition
            if not game_state["bricks"]:
                game_state["game_over"] = True

        draw_game(game_win, game_state)
        time.sleep(0.05)  # Faster ball speed

def input_thread(game_win, game_state, pause_event):
    while not game_state["game_over"]:
        key = game_win.getch()

        if key != -1:
            if key == curses.KEY_LEFT and game_state["paddle_x"] > 1:
                game_state["paddle_x"] -= 3  # Faster paddle movement
            elif key == curses.KEY_RIGHT and game_state["paddle_x"] + 15 < game_win.getmaxyx()[1] - 1:
                game_state["paddle_x"] += 3  # Faster paddle movement
            elif key == ord('q'):  # Quit the game
                game_state["game_over"] = True
            elif key == ord('p'):  # Pause the game
                game_state["paused"] = not game_state["paused"]
                if game_state["paused"]:
                    pause_event.set()  # Pause ball movement
                else:
                    pause_event.clear()  # Resume ball movement

def breakout(stdscr):
    stdscr = init_screen()
    height, width = 30, stdscr.getmaxyx()[1]  # Set height to 30, width to terminal width

    # Create a new window with fixed height
    game_win = curses.newwin(height, width, 0, 0)
    game_win.keypad(True)
    # Adjusted bricks for easier gameplay
    game_state = {
        "paddle_x": width // 2 - 7,  # Starting position of paddle (adjusted for longer paddle)
        "ball_x": width // 2,
        "ball_y": height // 2,
        "ball_dir_x": random.choice([-1, 1]),
        "ball_dir_y": -1,
        "bricks": [(y, x) for y in range(3, 15, 3) for x in range(4, width - 4, 8)],  # 4 lines of bricks
        "score": 0,
        "lives": 5,  # Increased lives for easier gameplay
        "game_over": False,
        "paused": False,
    }

    pause_event = threading.Event()

    # Create input and ball movement threads
    input_thread_instance = threading.Thread(target=input_thread, args=(game_win, game_state, pause_event))
    ball_thread_instance = threading.Thread(target=move_ball, args=(game_win, game_state, height, width, pause_event))

    # Start the threads
    input_thread_instance.start()
    ball_thread_instance.start()

    # Wait for threads to finish
    input_thread_instance.join()
    ball_thread_instance.join()

    # Game Over message
    game_win.addstr(height // 2, width // 2 - 5, "Game Over!" if game_state["lives"] == 0 else "You Win!")
    game_win.refresh()
    time.sleep(2)

curses.wrapper(breakout)
