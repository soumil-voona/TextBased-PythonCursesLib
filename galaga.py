import curses
import time
import random

def main(stdscr):
    # Initialize curses settings
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100)
    sh, sw = stdscr.getmaxyx()
    player_x = sw // 2
    player_y = sh - 2
    bullets = []
    enemies = []
    enemy_direction = 1  # Define enemy_direction here
    enemy_bullets = []
    score = 0
    level = 1
    lives = 3
    last_shot_time = 0
    shooting_cooldown = 0.2  # Cooldown in seconds
    powerups = []
    shield_active = False
    shield_end_time = 0
    combo = 0
    combo_end_time = 0
    boss_active = False
    boss_health = 0
    boss_x = sw // 2
    boss_y = 2
    boss_direction = 1

    # ASCII art for player, enemies, and boss
    PLAYER_ART = [" A ", "/|\\"]
    ENEMY_ART = ["MMM"]
    BOSS_ART = ["|===|", "| B |", "|===|"]

    def spawn_enemies():
        nonlocal enemies
        enemies = [[x, y] for y in range(2, 4) for x in range(15, sw - 15, 10)]

    def spawn_boss():
        nonlocal boss_active, boss_health, boss_x, boss_y
        boss_active = True
        boss_health = 50 + level * 10
        boss_x = sw // 2
        boss_y = 2

    def spawn_powerup(x, y):
        powerups.append([x, y, random.choice(["S", "F", "M"])])  # S: Shield, F: Fast shooting, M: Multi-shot

    def draw_entity(x, y, art):
        for i, line in enumerate(art):
            stdscr.addstr(y + i, x - len(line) // 2, line)

    def handle_input():
        nonlocal player_x, last_shot_time, shield_active
        key = stdscr.getch()
        if key == curses.KEY_LEFT and player_x > 2:
            player_x -= 2
        elif key == curses.KEY_RIGHT and player_x < sw - 3:
            player_x += 2
        elif key == ord(' '):
            current_time = time.time()
            if current_time - last_shot_time >= shooting_cooldown:
                bullets.append([player_x, player_y - 1])
                last_shot_time = current_time
                curses.beep()  # Shooting sound
        elif key == ord('p'):  # Pause game
            stdscr.addstr(sh // 2, sw // 2 - 5, "PAUSED")
            stdscr.refresh()
            while stdscr.getch() != ord('p'):
                pass

    def update_game():
        nonlocal player_x, bullets, enemies, enemy_bullets, score, lives, shield_active, shield_end_time, combo, combo_end_time, boss_active, boss_health, boss_x, boss_y, boss_direction, level, enemy_direction, powerups

        # Move bullets
        bullets = [[bx, by - 1] for bx, by in bullets if by > 1]

        # Move enemies
        move_down = False
        for i, (ex, ey) in enumerate(enemies):
            if ex + enemy_direction * 2 >= sw - 3 or ex + enemy_direction * 2 <= 2:
                move_down = True
                break

        if move_down:
            enemy_direction *= -1
            enemies = [[ex, ey + 1] for ex, ey in enemies]
        else:
            enemies = [[ex + enemy_direction * 2, ey] for ex, ey in enemies]

        # Enemy shooting
        if random.random() < 0.05 and enemies:
            shooter = random.choice(enemies)
            enemy_bullets.append([shooter[0], shooter[1] + 1])

        # Move enemy bullets
        enemy_bullets = [[ebx, eby + 1] for ebx, eby in enemy_bullets if eby < sh - 1]

        # Move power-ups downward
        powerups = [[px, py + 1, pt] for px, py, pt in powerups if py + 1 < sh - 1]

        # Collision detection for player bullets
        for bullet in bullets[:]:
            for enemy in enemies[:]:
                if enemy[0] - 1 <= bullet[0] <= enemy[0] + 1 and bullet[1] == enemy[1]:
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 10 * (1 + combo // 5)
                    combo += 1
                    combo_end_time = time.time() + 2  # Combo lasts 2 seconds
                    if random.random() < 0.1:  # 10% chance to drop power-up
                        spawn_powerup(enemy[0], enemy[1])
                    break

        # Collision detection for enemy bullets
        for ebx, eby in enemy_bullets[:]:
            if player_x - 1 <= ebx <= player_x + 1 and eby == player_y:
                if shield_active:
                    shield_active = False
                else:
                    lives -= 1
                    if lives <= 0:
                        game_over()
                        return
                enemy_bullets.remove([ebx, eby])

        # Collision detection for power-ups
        for px, py, pt in powerups[:]:
            if player_x - 1 <= px <= player_x + 1 and py == player_y:
                if pt == "F":
                    shooting_cooldown = 0.1  # Faster shooting
                elif pt == "S":
                    shield_active = True
                    shield_end_time = time.time() + 5  # Shield lasts 5 seconds
                elif pt == "M":
                    bullets.append([player_x - 1, player_y - 1])  # Left bullet
                    bullets.append([player_x + 1, player_y - 1])  # Right bullet
                powerups.remove([px, py, pt])  # Remove the collected power-up

        # Check if enemies reach the bottom
        if any(ey >= sh - 2 for _, ey in enemies):
            lives -= 1
            if lives <= 0:
                game_over()
                return
            else:
                spawn_enemies()

        # Level progression
        if not enemies and not boss_active:
            level += 1
            if level % 3 == 0:  # Spawn boss every 3 levels
                spawn_boss()
            else:
                spawn_enemies()
    def game_over():
        stdscr.addstr(sh // 2, sw // 2 - 5, "GAME OVER")
        stdscr.addstr(sh // 2 + 1, sw // 2 - 8, f"Final Score: {score}")
        stdscr.refresh()
        time.sleep(3)
        exit()

    spawn_enemies()

    while True:
        stdscr.clear()
        # Draw player
        draw_entity(player_x, player_y, PLAYER_ART)
        
        # Draw bullets
        for bx, by in bullets:
            stdscr.addstr(by, bx - 1, "||")
        
        # Draw enemies
        for ex, ey in enemies:
            draw_entity(ex, ey, ENEMY_ART)
        
        # Draw boss
        if boss_active:
            draw_entity(boss_x, boss_y, BOSS_ART)
        
        # Draw power-ups
        for px, py, pt in powerups:
            stdscr.addstr(py, px, pt)
        
        # Display score, level, and lives
        stdscr.addstr(0, 0, f"Score: {score}  Level: {level}  Lives: {lives}  Combo: {combo}x")
        
        # Handle input
        handle_input()
        
        # Update game state
        update_game()
        
        # Refresh screen
        stdscr.refresh()
        time.sleep(0.1)

curses.wrapper(main)