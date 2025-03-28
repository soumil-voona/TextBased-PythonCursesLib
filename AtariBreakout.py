import curses
import json
import time
import random
import threading

def init_screen():
    stdscr = curses.initscr()
    curses.curs_set(0)
    stdscr.keypad(True)
    curses.noecho()
    curses.cbreak()

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_GREEN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_CYAN, -1)

    return stdscr

def draw_game(game_win, game_state):
    game_win.clear()
    game_win.border(0)

    height, width = game_win.getmaxyx()

    game_win.attron(curses.color_pair(1))
    for y, x in game_state["bricks"]:
        if 0 <= y < height and 0 <= x < width:
            for i in range(4):
                if x + i < width:
                    game_win.addch(y, x + i, "#")
    game_win.attroff(curses.color_pair(1))

    game_win.attron(curses.color_pair(2))
    paddle_y = height - 2
    for i in range(15):
        paddle_x = game_state["paddle_x"] + i
        if 0 <= paddle_x < width - 1:
            game_win.addch(paddle_y, paddle_x, "=")
    game_win.attroff(curses.color_pair(2))

    game_win.attron(curses.color_pair(3))
    ball_y, ball_x = int(game_state["ball_y"]), int(game_state["ball_x"])
    if 0 <= ball_y < height - 1 and 0 <= ball_x < width - 1:
        game_win.addstr(ball_y, ball_x, "*")
        game_win.addstr(ball_y, ball_x + 1, "*")
        game_win.addstr(ball_y + 1, ball_x, "*")
        game_win.addstr(ball_y + 1, ball_x + 1, "*")
    game_win.attroff(curses.color_pair(3))

    game_win.addstr(0, 2, f"Score: {game_state['score']}  Lives: {game_state['lives']}")

    if game_state["paused"]:
        game_win.attron(curses.color_pair(4))
        game_win.addstr(height // 2, width // 2 - 3, "Paused")
        game_win.attroff(curses.color_pair(4))

    game_win.refresh()

def move_ball(game_win, game_state, height, width, pause_event):
    ASCII_ART = [
        "              ________  _________  ________  ________  ___",                          
        "             |\\   __  \\|\\___   ___\\\\   __  \\|\\   __  \\|\\  \\",                         
        "             \\ \\  \\|\\  \\|___ \\  \\_\\ \\  \\|\\  \\ \\  \\|\\  \\ \\  \\",                        
        "              \\ \\   __  \\   \\ \\  \\ \\ \\   __  \\ \\   _  _\\ \\  \\",                       
        "               \\ \\  \\ \\  \\   \\ \\  \\ \\ \\  \\ \\  \\ \\  \\\\  \\\\ \\  \\",                      
        "                \\ \\__\\ \\__\\   \\ \\__\\ \\ \\__\\ \\__\\ \\__\\\\ _\\\\ \\__\\",                     
        "                 \\|__|\\|__|    \\|__|  \\|__|\\|__|\\|__|\\|__|\\|__|",                                                                                               
        " ________  ________  _______   ________  ___  __    ________  ___  ___  _________",   
        "|\\   __  \\|\\   __  \\|\\  ___ \\ |\\   __  \\|\\  \\|\\  \\ |\\   __  \\|\\  \\|\\  \\|\\___   ___\\", 
        "\\ \\  \\|\\ /\\ \\  \\|\\  \\ \\   __/|\\ \\  \\|\\  \\ \\  \\/  /|\\ \\  \\|\\  \\ \\  \\\\\\  \\|___ \\  \\_|", 
        " \\ \\   __  \\ \\   _  _\\ \\  \\_|/_\\ \\   __  \\ \\   ___  \\ \\  \\\\\\  \\ \\  \\\\\\  \\   \\ \\  \\",  
        "  \\ \\  \\|\\  \\ \\  \\\\  \\\\ \\  \\_|\\ \\ \\  \\ \\  \\ \\  \\\\ \\  \\ \\  \\\\\\  \\ \\  \\\\\\  \\   \\ \\  \\",
        "   \\ \\_______\\ \\__\\\\ _\\\\ \\_______\\ \\__\\ \\__\\ \\__\\\\ \\__\\ \\_______\\ \\_______\\   \\ \\__\\",
        "    \\|_______|\\|__|\\|__|\\|_______|\\|__|\\|__|\\|__| \\|__|\\|_______|\\|_______|    \\|__|"
    ]
    y = height // 2 - 10
    
    for line in ASCII_ART:
        game_win.addstr(y, width // 2 - 42, line)
        y += 1
    game_win.refresh()
    time.sleep(2)

    game_win.clear()
    instructions = [
        "***********************************************************************",
        "*                           Instructions:                             *",
        "* 1. Use the LEFT and RIGHT arrow keys to move the paddle             *",
        "* 2. Your goal is to break all of the bricks without losing all lives *",
        "* 3. You will have 5 lives to try to destroy all the bricks           *",
        "* 4. Press the q key to exit at any time, p to pause                  *",
        "*                                                                     *",
        "*                    Press ENTER to start the game                    *",
        "***********************************************************************"
    ]
    for i, line in enumerate(instructions):
        game_win.addstr(height // 2 - 4 + i, width // 2 - len(line) // 2, line)
    game_win.refresh()
    
    while True:
        key = game_win.getch()
        if key == 27:
            return
        if key == 10:
            break

    while not game_state["game_over"]:
        if not game_state["paused"]:
            prev_y = game_state["ball_y"]
            prev_x = game_state["ball_x"]
            
            game_state["ball_y"] += game_state["ball_dir_y"]
            game_state["ball_x"] += game_state["ball_dir_x"]

            if game_state["ball_x"] <= 1:
                game_state["ball_x"] = 2
                game_state["ball_dir_x"] *= -1
            elif game_state["ball_x"] >= width - 3:
                game_state["ball_x"] = width - 3
                game_state["ball_dir_x"] *= -1

            if game_state["ball_y"] <= 1:
                game_state["ball_y"] = 2
                game_state["ball_dir_y"] *= -1

            paddle_top = height - 3
            paddle_left = game_state["paddle_x"]
            paddle_right = game_state["paddle_x"] + 15

            if (game_state["ball_y"] >= paddle_top - 1 and prev_y < paddle_top - 1 and 
                game_state["ball_dir_y"] > 0):
                if paddle_left - 1 <= game_state["ball_x"] <= paddle_right:
                    game_state["ball_y"] = paddle_top - 2
                    game_state["ball_dir_y"] *= -1
                    
                    paddle_center = paddle_left + 7.5
                    hit_position = game_state["ball_x"] - paddle_left
                    
                    if hit_position < 3:
                        game_state["ball_dir_x"] = -1.5
                    elif hit_position < 6:
                        game_state["ball_dir_x"] = -1.0
                    elif hit_position < 9:
                        game_state["ball_dir_x"] = 0
                    elif hit_position < 12:
                        game_state["ball_dir_x"] = 1.0
                    else:
                        game_state["ball_dir_x"] = 1.5

            new_bricks = []
            ball_hit_brick = False
            
            next_ball_y = int(game_state["ball_y"] + game_state["ball_dir_y"])
            next_ball_x = int(game_state["ball_x"] + game_state["ball_dir_x"])
            
            ball_left = next_ball_x
            ball_right = next_ball_x + 1
            ball_top = next_ball_y
            ball_bottom = next_ball_y + 1

            for y, x in game_state["bricks"]:
                brick_left = x
                brick_right = x + 3
                brick_top = y
                brick_bottom = y

                if not (ball_right < brick_left or     
                        ball_left > brick_right or     
                        ball_bottom < brick_top or     
                        ball_top > brick_bottom):      
                    if not ball_hit_brick:
                        game_state["ball_dir_y"] *= -1
                        ball_hit_brick = True
                    game_state["score"] += 10
                else:
                    new_bricks.append((y, x))
            
            game_state["bricks"] = new_bricks

            if int(game_state["ball_y"]) >= height - 2:
                game_state["lives"] -= 1
                if game_state["lives"] <= 0:
                    game_state["game_over"] = True
                else:
                    game_state["ball_y"] = height - 4
                    game_state["ball_x"] = width // 2
                    game_state["ball_dir_y"] = -1
                    game_state["ball_dir_x"] = random.choice([-1, -0.5, 0.5, 1])
                    game_state["paddle_x"] = width // 2 - 7

            if not game_state["bricks"]:
                game_state["game_over"] = True

        draw_game(game_win, game_state)
        time.sleep(0.07)

def input_thread(game_win, game_state, pause_event):
    while not game_state["game_over"]:
        key = game_win.getch()

        if key != -1:
            if key == curses.KEY_LEFT and game_state["paddle_x"] > 1:
                game_state["paddle_x"] -= 4
            elif key == curses.KEY_RIGHT and game_state["paddle_x"] + 15 < game_win.getmaxyx()[1] - 1:
                game_state["paddle_x"] += 4
            elif key == ord('q'):
                game_state["game_over"] = True
            elif key == ord('p'):
                game_state["paused"] = not game_state["paused"]
                if game_state["paused"]:
                    pause_event.set()
                else:
                    pause_event.clear()

def init_leaderboard():
    try:
        with open('breakout_leaderboard.json', 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open('breakout_leaderboard.json', 'w') as f:
            json.dump([], f)
        return []

def breakout(stdscr):
    stdscr = init_screen()
    height, width = 30, stdscr.getmaxyx()[1]

    game_win = curses.newwin(height, width, 0, 0)
    game_win.keypad(True)
    
    game_state = {
        "paddle_x": width // 2 - 7,
        "ball_x": width // 2,
        "ball_y": height // 2,
        "ball_dir_x": random.choice([-1, 1]),
        "ball_dir_y": -1,
        "bricks": [(y, x) for y in range(3, 15, 3) for x in range(4, width - 4, 8)],
        "score": 0,
        "lives": 5,
        "game_over": False,
        "paused": False,
    }

    pause_event = threading.Event()

    input_thread_instance = threading.Thread(target=input_thread, args=(game_win, game_state, pause_event))
    ball_thread_instance = threading.Thread(target=move_ball, args=(game_win, game_state, height, width, pause_event))

    input_thread_instance.start()
    ball_thread_instance.start()

    input_thread_instance.join()
    ball_thread_instance.join()

    game_win.addstr(height // 2, width // 2 - 5, "Game Over!" if game_state["lives"] == 0 else "You Win!")
    game_win.refresh()
    
    leaderboard = init_leaderboard()
    
    game_win.addstr(height // 2 + 2, width // 2 - 15, "Enter your name: ")
    game_win.refresh()
    curses.echo()
    player_name = game_win.getstr(height // 2 + 2, width // 2 + 2, 20).decode('utf-8')
    curses.noecho()
    
    if not player_name.strip():
        player_name = "Player"
    leaderboard.append((player_name, game_state["score"]))
    leaderboard.sort(key=lambda x: x[1], reverse=True)
    leaderboard = leaderboard[:10]
    
    with open('breakout_leaderboard.json', 'w') as f:
        json.dump(leaderboard, f)
    
    game_win.addstr(height // 2 + 2, width // 2 - 10, "Leaderboard:")
    for i, (name, score) in enumerate(leaderboard):
        game_win.addstr(height // 2 + 4 + i, width // 2 - 10, f"{i+1}. {name}: {score}")
    game_win.refresh()
    time.sleep(2)

curses.wrapper(breakout)
