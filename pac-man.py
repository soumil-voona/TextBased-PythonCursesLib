import curses
import time
import random

# Initialize the screen
stdscr = curses.initscr()
curses.curs_set(0)  # Hide cursor
stdscr.keypad(1)  # Enable keypad input for arrow key handling
curses.start_color()  # Start color
stdscr.timeout(100)  # Refresh every 100 milliseconds

# Initialize colors
curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Pac-Man color (Yellow)
curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)    # Ghost color (Cyan)
curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)      # Wall color (Red)
curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)    # Dot color (White)
curses.init_pair(5, curses.COLOR_BLUE, curses.COLOR_BLACK)     # Weak Ghost color (Blue)

# Game variables
maze = [
    "############################",
    "#O............#...........O#",
    "#.####.#.#.#.####.#.#.#.##.#",
    "#.#..#.#.#.#..#.#..#.#.#...#",
    "#.#..#.#.#.#..#.#..#.#.#...#",
    "#.####.#.#.#.####.#.#.#.##.#",
    "#..........................#",
    "#.####.#.#.#.####.#.#.#.##.#",
    "#.#........................#",
    "#.#.###########.#.#.#.#.#..#",
    "#.#...............#........#",
    "#.#.#.###########.#.#.#.#..#",
    "#.................#........#",
    "#.####.#.#.#.####.#.#.#.##.#",
    "#O.......................O.#",
    "############################"
]
maze_height = len(maze)
maze_width = len(maze[0])

# Create game window
game_window = curses.newwin(maze_height + 1, maze_width + 1, 0, 0)
game_window.keypad(True)  # Enable keypad input

# Player settings
player_x, player_y = 1, 1
player_char = "C"
mouth_open = True
direction = "right"

# Ghost settings
ghosts = [
    {"x": 10, "y": 5, "char": "G", "color": 2, "weak": False},
    {"x": 15, "y": 10, "char": "G", "color": 2, "weak": False}
]

# Game state
score = 0
lives = 3
powered_up = False
power_up_timer = 0

# Function to draw the maze
def draw_maze():
    for y in range(maze_height):
        for x in range(maze_width):
            if maze[y][x] == "#":
                game_window.attron(curses.color_pair(3))
                game_window.addch(y, x, "#")
                game_window.attroff(curses.color_pair(3))
            elif maze[y][x] == ".":
                game_window.attron(curses.color_pair(4))
                game_window.addch(y, x, ".")
                game_window.attroff(curses.color_pair(4))
            elif maze[y][x] == "O":  # Power Pellet
                game_window.attron(curses.color_pair(5))
                game_window.addch(y, x, "O")
                game_window.attroff(curses.color_pair(5))

# Function to move ghosts (simple AI)
def move_ghosts():
    for ghost in ghosts:
        move = random.choice(["x", "y"])
        if move == "x":
            if ghost["x"] < player_x and maze[ghost["y"]][ghost["x"] + 1] != "#":
                ghost["x"] += 1
            elif ghost["x"] > player_x and maze[ghost["y"]][ghost["x"] - 1] != "#":
                ghost["x"] -= 1
        elif move == "y":
            if ghost["y"] < player_y and maze[ghost["y"] + 1][ghost["x"]] != "#":
                ghost["y"] += 1
            elif ghost["y"] > player_y and maze[ghost["y"] - 1][ghost["x"]] != "#":
                ghost["y"] -= 1

# Function to check if Pac-Man collides with a ghost
def check_collision():
    global lives, score
    for ghost in ghosts:
        if ghost["x"] == player_x and ghost["y"] == player_y:
            if ghost["weak"]:  # If ghost is weak, Pac-Man eats it
                score += 200
                ghost["x"], ghost["y"] = 10, 5  # Reset ghost position
                ghost["weak"] = False
            else:
                lives -= 1
                return True
    return False

# Function to determine Pac-Man's mouth shape
def get_pacman_char(direction):
    global mouth_open
    mouth_open = not mouth_open
    return "C" if mouth_open else "c"

# Main game loop
while True:
    game_window.clear()
    draw_maze()

    # Handle power-up mode
    if powered_up:
        power_up_timer -= 1
        if power_up_timer <= 0:
            powered_up = False
            for ghost in ghosts:
                ghost["weak"] = False

    # Draw Pac-Man
    pacman_char = get_pacman_char(direction)
    game_window.attron(curses.color_pair(1))
    game_window.addch(player_y, player_x, pacman_char)
    game_window.attroff(curses.color_pair(1))

    # Move and draw ghosts
    move_ghosts()
    for ghost in ghosts:
        game_window.attron(curses.color_pair(5 if ghost["weak"] else ghost["color"]))
        game_window.addch(ghost["y"], ghost["x"], "V" if ghost["weak"] else "G")
        game_window.attroff(curses.color_pair(5 if ghost["weak"] else ghost["color"]))

    # Display score and lives
    game_window.addstr(maze_height, 1, f"Score: {score}  Lives: {lives}")

    # Refresh the screen
    game_window.refresh()

    # Get user input
    key = game_window.getch()

    # Move player
    if key == curses.KEY_RIGHT and maze[player_y][player_x + 1] != "#":
        player_x += 1
        direction = "right"
    elif key == curses.KEY_LEFT and maze[player_y][player_x - 1] != "#":
        player_x -= 1
        direction = "left"
    elif key == curses.KEY_UP and maze[player_y - 1][player_x] != "#":
        player_y -= 1
        direction = "up"
    elif key == curses.KEY_DOWN and maze[player_y + 1][player_x] != "#":
        player_y += 1
        direction = "down"
    elif key == ord('q'):  # Quit
        break

    # Check for dot collection
    if maze[player_y][player_x] == ".":
        score += 10
        maze[player_y] = maze[player_y][:player_x] + " " + maze[player_y][player_x + 1:]

    # Check for power pellet
    if maze[player_y][player_x] == "O":
        powered_up = True
        power_up_timer = 50  # Power lasts for 5 seconds
        for ghost in ghosts:
            ghost["weak"] = True
        maze[player_y] = maze[player_y][:player_x] + " " + maze[player_y][player_x + 1:]

    # Check for collisions
    if check_collision() and lives == 0:
        game_window.addstr(maze_height // 2, maze_width // 2 - 5, "Game Over!")
        game_window.refresh()
        time.sleep(2)
        break

curses.endwin()
