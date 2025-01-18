#PAC-MAZE-MANIA
import pygame
import random
import heapq

# Initialize Pygame
pygame.init()

# Grid and Screen Setup
GRID_CELL = 20
GRID_COLS, GRID_ROWS = 28, 31
WINDOW_WIDTH, WINDOW_HEIGHT = GRID_COLS * GRID_CELL, GRID_ROWS * GRID_CELL
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Pac Maze Mania")

# Colors
COLOR_BG = (10, 10, 10)
COLOR_WALL = (0, 0, 200)
COLOR_PELLET = (200, 200, 200)
COLOR_PACMAN = (255, 255, 0)
COLOR_GHOST = {"aggressive": (200, 0, 0), "random": (0, 200, 200)}

# FPS Controller
fps = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)

# Game Grid: Randomize walls (1 = wall, 0 = pellet)
game_map = [[1 if random.random() < 0.2 else 0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]

# Pac-Man
player_position = [1, 1]
player_speed = 1

# Ghosts Configuration
ghosts = [
    {"position": [GRID_COLS - 3, 1], "type": "aggressive"},
    {"position": [1, GRID_ROWS - 5], "type": "random"}
]

# Pellet Tracking
pellets_remaining = sum(row.count(0) for row in game_map)

def render_map():
    """Draws the walls and pellets."""
    for row in range(GRID_ROWS):
        for col in range(GRID_COLS):
            rect = pygame.Rect(col * GRID_CELL, row * GRID_CELL, GRID_CELL, GRID_CELL)
            if game_map[row][col] == 1:
                pygame.draw.rect(screen, COLOR_WALL, rect)
            elif game_map[row][col] == 0:
                pygame.draw.circle(screen, COLOR_PELLET, rect.center, GRID_CELL // 4)

def render_player():
    """Draws Pac-Man."""
    rect = pygame.Rect(player_position[0] * GRID_CELL, player_position[1] * GRID_CELL, GRID_CELL, GRID_CELL)
    pygame.draw.circle(screen, COLOR_PACMAN, rect.center, GRID_CELL // 2)

def render_ghosts():
    """Draws the ghosts."""
    for ghost in ghosts:
        rect = pygame.Rect(ghost["position"][0] * GRID_CELL, ghost["position"][1] * GRID_CELL, GRID_CELL, GRID_CELL)
        pygame.draw.circle(screen, COLOR_GHOST[ghost["type"]], rect.center, GRID_CELL // 2)

def handle_player_input(keys):
    """Handles movement of Pac-Man."""
    new_position = list(player_position)
    if keys[pygame.K_UP]:
        new_position[1] -= player_speed
    if keys[pygame.K_DOWN]:
        new_position[1] += player_speed
    if keys[pygame.K_LEFT]:
        new_position[0] -= player_speed
    if keys[pygame.K_RIGHT]:
        new_position[0] += player_speed

    # Wall Collision
    if game_map[new_position[1]][new_position[0]] != 1:
        player_position[:] = new_position

    # Collect Pellet
    if game_map[player_position[1]][player_position[0]] == 0:
        game_map[player_position[1]][player_position[0]] = 2
        return 10  # Points for eating a pellet
    return 0

def calculate_path(start, target):
    """Finds the shortest path using A*."""
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    heapq.heappush(open_set, (0, start))
    came_from = {}
    g_cost = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == target:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            return path[::-1]

        neighbors = [
            (current[0] + dx, current[1] + dy)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
        ]
        valid_neighbors = [n for n in neighbors if 0 <= n[0] < GRID_COLS and 0 <= n[1] < GRID_ROWS and game_map[n[1]][n[0]] != 1]

        for neighbor in valid_neighbors:
            temp_cost = g_cost[current] + 1
            if temp_cost < g_cost.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_cost[neighbor] = temp_cost
                priority = temp_cost + heuristic(neighbor, target)
                heapq.heappush(open_set, (priority, neighbor))

    return []

def update_ghosts():
    """Moves ghosts based on their strategies."""
    for ghost in ghosts:
        if ghost["type"] == "aggressive":
            path = calculate_path(tuple(ghost["position"]), tuple(player_position))
            if path:
                ghost["position"] = list(path[0])
        elif ghost["type"] == "random":
            direction = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
            new_pos = [ghost["position"][0] + direction[0], ghost["position"][1] + direction[1]]
            if 0 <= new_pos[0] < GRID_COLS and 0 <= new_pos[1] < GRID_ROWS and game_map[new_pos[1]][new_pos[0]] != 1:
                ghost["position"] = new_pos

# Main Game Loop
running = True
score = 0

while running:
    screen.fill(COLOR_BG)

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    score += handle_player_input(keys)
    update_ghosts()

    # Render Game Elements
    render_map()
    render_player()
    render_ghosts()

    # Display Score
    score_display = font.render(f"Score: {score}", True, COLOR_PELLET)
    screen.blit(score_display, (10, 10))

    # Win/Loss Check
    if all(game_map[row][col] != 0 for row in range(GRID_ROWS) for col in range(GRID_COLS)):
        print("You Win!")
        running = False

    for ghost in ghosts:
        if ghost["position"] == player_position:
            print("Game Over!")
            running = False

    pygame.display.flip()
    fps.tick(10)
