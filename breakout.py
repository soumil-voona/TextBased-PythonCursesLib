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
            for i in range(4):  # 4x1 bricks
                if 0 <= y < height and 0 <= x + i < width:
                    game_win.addch(y, x + i, "#")
    game_win.attroff(curses.color_pair(1))

    # Draw paddle
    game_win.attron(curses.color_pair(2))
    paddle_y = height - 2
    for i in range(10):  # Increased paddle size to make it easier
        paddle_x = game_state["paddle_x"] + i
        if 0 <= paddle_x < width - 1:
            game_win.addch(paddle_y, paddle_x, "=")
    game_win.attroff(curses.color_pair(2))

    # Draw ball
    game_win.attron(curses.color_pair(3))
    ball_y, ball_x = game_state["ball_y"], game_state["ball_x"]
    if 0 <= ball_y < height and 0 <= ball_x < width:
        game_win.addch(ball_y, ball_x, "O")
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
            game_state["ball_y"] += game_state["ball_dir_y"]
            game_state["ball_x"] += game_state["ball_dir_x"]

            # Ball collision with walls
            if game_state["ball_x"] <= 1 or game_state["ball_x"] >= width - 2:
                game_state["ball_dir_x"] *= -1

            if game_state["ball_y"] <= 1:
                game_state["ball_dir_y"] *= -1

            # Ball collision with paddle
            if game_state["ball_y"] == height - 3 and game_state["paddle_x"] <= game_state["ball_x"] < game_state["paddle_x"] + 10:
                game_state["ball_dir_y"] *= -1
                # Ball reflects at an angle based on where it hits the paddle
                paddle_hit_position = game_state["ball_x"] - game_state["paddle_x"]
                if paddle_hit_position < 3:
                    game_state["ball_dir_x"] = -1
                elif paddle_hit_position > 6:
                    game_state["ball_dir_x"] = 1
                else:
                    game_state["ball_dir_x"] = 0

            # Ball collision with bricks
            new_bricks = []
            for y, x in game_state["bricks"]:
                if (y <= game_state["ball_y"] <= y and
                    x <= game_state["ball_x"] <= x + 3):  # Updated to handle 4x1 bricks
                    game_state["ball_dir_y"] *= -1
                    game_state["score"] += 10
                else:
                    new_bricks.append((y, x))
            game_state["bricks"] = new_bricks

            # Ball falls below paddle
            if game_state["ball_y"] >= height - 1:
                game_state["lives"] -= 1
                if game_state["lives"] == 0:
                    game_state["game_over"] = True
                else:
                    game_state["ball_y"], game_state["ball_x"] = height - 4, width // 2
                    game_state["ball_dir_y"], game_state["ball_dir_x"] = -1, random.choice([-1, 1])

            # Check win condition
            if not game_state["bricks"]:
                game_state["game_over"] = True

        draw_game(game_win, game_state)
        time.sleep(0.1)  # Adjusted speed for better control

def input_thread(game_win, game_state, pause_event):
    while not game_state["game_over"]:
        key = game_win.getch()

        if key != -1:
            if key == curses.KEY_LEFT and game_state["paddle_x"] > 1:
                game_state["paddle_x"] -= 4
            elif key == curses.KEY_RIGHT and game_state["paddle_x"] + 10 < game_win.getmaxyx()[1] - 1:
                game_state["paddle_x"] += 4
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
    height, width = stdscr.getmaxyx()

    # Adjusted bricks for easier gameplay
    game_state = {
        "paddle_x": width // 2 - 5,  # Starting position of paddle (adjusted for longer paddle)
        "ball_x": width // 2,
        "ball_y": 20,
        "ball_dir_x": random.choice([-1, 1]),
        "ball_dir_y": -1,
        "bricks": [(y, x) for y in range(3, 8, 3) for x in range(4, width - 4, 6)],  # Closer bricks
        "score": 0,
        "lives": 5,  # Increased lives for easier gameplay
        "game_over": False,
        "paused": False,
    }

    pause_event = threading.Event()

    # Create input and ball movement threads
    input_thread_instance = threading.Thread(target=input_thread, args=(stdscr, game_state, pause_event))
    ball_thread_instance = threading.Thread(target=move_ball, args=(stdscr, game_state, height, width, pause_event))

    # Start the threads
    input_thread_instance.start()
    ball_thread_instance.start()

    # Wait for threads to finish
    input_thread_instance.join()
    ball_thread_instance.join()

    # Game Over message
    stdscr.addstr(height // 2, width // 2 - 5, "Game Over!" if game_state["lives"] == 0 else "You Win!")
    stdscr.refresh()
    time.sleep(2)

curses.wrapper(breakout)
