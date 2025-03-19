import curses
import time
import random
import threading

def init_screen():
    stdscr = curses.initscr()
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.noecho()
    curses.cbreak()
    stdscr.nodelay(True)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()  # Ensure default background
        curses.init_pair(1, curses.COLOR_RED, -1)      # Bricks
        curses.init_pair(2, curses.COLOR_GREEN, -1)    # Paddle
        curses.init_pair(3, curses.COLOR_YELLOW, -1)   # Ball
        curses.init_pair(4, curses.COLOR_CYAN, -1)     # Pause Message
    return stdscr

def draw_game(stdscr, game_state):
    stdscr.clear()
    stdscr.border(0)

    height, width = stdscr.getmaxyx()

    # Draw bricks
    stdscr.attron(curses.color_pair(1))
    for y, x in game_state["bricks"]:
        if 0 <= y < height and 0 <= x < width: 
            for i in range(4):
                for j in range(2):
                    if 0 <= y + j < height and 0 <= x + i < width:
                        stdscr.addch(y + j, x + i, "#")
    stdscr.attroff(curses.color_pair(1))

    # Draw paddle
    stdscr.attron(curses.color_pair(2))
    paddle_y = height - 2
    for i in range(8):
        paddle_x = game_state["paddle_x"] + i
        if 0 <= paddle_x < width - 1:
            stdscr.addch(paddle_y, paddle_x, "=")
    stdscr.attroff(curses.color_pair(2))

    # Draw ball
    stdscr.attron(curses.color_pair(3))
    ball_y, ball_x = game_state["ball_y"], game_state["ball_x"]
    if 0 <= ball_y < height and 0 <= ball_x < width:
        stdscr.addch(ball_y, ball_x, "O")
    stdscr.attroff(curses.color_pair(3))

    # Display score and lives
    stdscr.addstr(0, 2, f"Score: {game_state['score']}  Lives: {game_state['lives']}")

    # Display pause message
    if game_state["paused"]:
        stdscr.attron(curses.color_pair(4))
        stdscr.addstr(height // 2, width // 2 - 3, "Paused")
        stdscr.attroff(curses.color_pair(4))

    stdscr.refresh()

def move_ball(stdscr, game_state, height, width):
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
            if (game_state["ball_y"] == height - 3 and
                game_state["paddle_x"] <= game_state["ball_x"] < game_state["paddle_x"] + 8):
                game_state["ball_dir_y"] *= -1
                game_state["ball_dir_x"] = random.choice([-1, 0, 1])

            # Ball collision with bricks
            new_bricks = []
            for y, x in game_state["bricks"]:
                if (y <= game_state["ball_y"] <= y + 1 and
                    x <= game_state["ball_x"] <= x + 3):
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

            draw_game(stdscr, game_state)
            time.sleep(0.1)
        else:
            time.sleep(0.1)

def breakout(stdscr):
    stdscr = init_screen()
    height, width = stdscr.getmaxyx()

    game_state = {
        "paddle_x": width // 2 - 4,
        "ball_x": width // 2,
        "ball_y": height - 4,
        "ball_dir_x": random.choice([-1, 1]),
        "ball_dir_y": -1,
        "bricks": [(y, x) for y in range(3, 12, 3) for x in range(4, width - 4, 8)],
        "score": 0,
        "lives": 3,
        "game_over": False,
        "paused": False,
    }

    ball_thread = threading.Thread(target=move_ball, args=(stdscr, game_state, height, width))
    ball_thread.daemon = True
    ball_thread.start()

    while not game_state["game_over"]:
        key = stdscr.getch()
        if key == curses.KEY_LEFT and game_state["paddle_x"] > 1:
            game_state["paddle_x"] -= 4
        elif key == curses.KEY_RIGHT and game_state["paddle_x"] + 8 < width - 1:
            game_state["paddle_x"] += 4
        elif key == ord('q'):
            game_state["game_over"] = True
        elif key == ord('p'):
            game_state["paused"] = not game_state["paused"]

        draw_game(stdscr, game_state)
        time.sleep(0.03)

    stdscr.addstr(height // 2, width // 2 - 5, "Game Over!" if game_state["lives"] == 0 else "You Win!")
    stdscr.refresh()
    time.sleep(2)

curses.wrapper(breakout)
