import pygame
import random
import sys
import heapq

# COULEURS
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NEON = (26, 192, 207)

# CONSTANTES
WIDTH, HEIGHT = 1400, 900  # Taille de la fenêtre agrandie
FPS = 60
GAME_SIZE = 3
TILE_SIZE = 250  # Taille des tuiles agrandie

screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Définition de la police et création d'une surface avec le message
pygame.font.init()
font = pygame.font.SysFont(None, 50)
win_message = font.render("Congratulations! You won!", True, BLACK)
win_message_rect = win_message.get_rect(center=(WIDTH // 2, HEIGHT // 4))

# Chargement des images
Shuffle_Button = pygame.image.load("assets/SHUFFLEBUTTON.png")
Reset_Button = pygame.image.load("assets/reset.png")
BFS_Button = pygame.image.load("assets/bfs.png")
A_etoile = pygame.image.load("assets/A_etoile.png")

message = pygame.image.load("assets/reset_message.png")

image1 = pygame.image.load("assets/1.png")
image2 = pygame.image.load("assets/2.png")
image3 = pygame.image.load("assets/3.png")
image4 = pygame.image.load("assets/4.png")
image5 = pygame.image.load("assets/5.png")
image6 = pygame.image.load("assets/6.png")
image7 = pygame.image.load("assets/7.png")
image8 = pygame.image.load("assets/8.png")
empty_image = pygame.image.load("assets/empty.png")
images = {0: empty_image, 1: image1, 2: image2, 3: image3, 4: image4, 5: image5, 6: image6, 7: image7, 8: image8}


class Button:
    def __init__(self, image, position):
        self.image = image
        self.rect = self.image.get_rect(center=position)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0] == 1


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("8-puzzle game")
        self.clock = pygame.time.Clock()
        self.player_grid = self.create_grid()
        self.completed_grid = self.create_grid()
        self.shuffle_once = False
        self.shuffled_grids = []

    def create_grid(self):
        GRID = []
        CELL_NUM = 1
        for row in range(GAME_SIZE):
            GRID.append([])
            for col in range(GAME_SIZE):
                GRID[row].append(CELL_NUM)
                CELL_NUM += 1
        GRID[2][2] = 0
        return GRID

    def draw_grid(self):
        grid_top_left_x = (WIDTH - GAME_SIZE * TILE_SIZE) // 2
        grid_top_left_y = (HEIGHT - GAME_SIZE * TILE_SIZE) // 2
        for horz_line in range(-1, GAME_SIZE * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(screen, BLACK, (grid_top_left_x + horz_line, grid_top_left_y),
                             (grid_top_left_x + horz_line, grid_top_left_y + GAME_SIZE * TILE_SIZE))
        for vert_line in range(-1, GAME_SIZE * TILE_SIZE, TILE_SIZE):
            pygame.draw.line(screen, BLACK, (grid_top_left_x, grid_top_left_y + vert_line),
                             (grid_top_left_x + GAME_SIZE * TILE_SIZE, grid_top_left_y + vert_line))

    def draw_tiles(self):
        grid_top_left_x = (WIDTH - GAME_SIZE * TILE_SIZE) // 2
        grid_top_left_y = (HEIGHT - GAME_SIZE * TILE_SIZE) // 2
        for row, list_row in enumerate(self.player_grid):
            for col, element in enumerate(list_row):
                for i in (images.keys()):
                    if element == i:
                        self.rect = images[i].get_rect()
                        self.rect.x = grid_top_left_x + col * TILE_SIZE + TILE_SIZE / 2 - self.rect.width / 2
                        self.rect.y = grid_top_left_y + row * TILE_SIZE + TILE_SIZE / 2 - self.rect.height / 2
                        screen.blit(images[i], (self.rect.x, self.rect.y))

    def update(self, x, y):
        self.rect.x = x * TILE_SIZE
        self.rect.y = y * TILE_SIZE

    def valid_move(self, row, col):
        empty_x, empty_y = self.find_empty_tile(self.player_grid)
        return (row == empty_x and abs(col - empty_y) == 1) or (col == empty_y and abs(row - empty_x) == 1)

    def clicked_tile(self, mouse_x, mouse_y):
        x = mouse_y // TILE_SIZE
        y = mouse_x // TILE_SIZE
        return x, y

    def find_empty_tile(self, grid):
        for x, list_row in enumerate(grid):
            for y, element in enumerate(list_row):
                if element == 0:
                    return x, y

    def handle_move(self, tile_x, tile_y):
        empty_x, empty_y = self.find_empty_tile(self.player_grid)
        if self.valid_move(tile_x, tile_y):
            self.player_grid[empty_x][empty_y] = self.player_grid[tile_x][tile_y]
            self.player_grid[tile_x][tile_y] = 0
        draw_all()

    def shuffle(self):
        reset_button.image = Reset_Button
        for i in range(99):
            empty_x, empty_y = self.find_empty_tile(self.player_grid)
            directions = [(empty_x + 1, empty_y), (empty_x - 1, empty_y), (empty_x, empty_y + 1),
                          (empty_x, empty_y - 1)]
            valid_moves = [(x, y) for x, y in directions if 0 <= x <= 2 and 0 <= y <= 2]
            next_x, next_y = random.choice(valid_moves)
            self.handle_move(next_x, next_y)
        self.shuffle_once = True
        shuffle_grid = [row[:] for row in self.player_grid]
        self.shuffled_grids.append(shuffle_grid)

    def win(self):
        return self.player_grid == self.completed_grid

    def reset(self):
        if self.shuffle_once:
            if self.shuffled_grids == []:
                reset_button.image = message
            else:
                self.player_grid = self.shuffled_grids[0]
                self.shuffled_grids = []

    def a_etoile_solution(self):
        current_grid = [row[:] for row in self.player_grid]
        depth = 0
        visited = set()
        priority_queue = [(self.evaluate_state2(current_grid, depth), current_grid, [])]

        while priority_queue:
            _, grid, path = heapq.heappop(priority_queue)
            visited.add(tuple(map(tuple, grid)))

            if self.evaluate_state(grid) == 0:
                return path

            neighbors = self.generate_grids(grid)
            depth += 1
            for neighbor in neighbors:
                if tuple(map(tuple, neighbor)) not in visited:
                    heapq.heappush(priority_queue,
                                   (self.evaluate_state2(neighbor, depth), neighbor, path + [neighbor]))
        return None

    def bfs_solution(self):
        current_grid = [row[:] for row in self.player_grid]
        visited = set()
        priority_queue = [(self.evaluate_state(current_grid), current_grid, [])]

        while priority_queue:
            _, grid, path = heapq.heappop(priority_queue)
            visited.add(tuple(map(tuple, grid)))  # Convertir la grille en tuple pour vérifier la visite

            if self.evaluate_state(grid) == 0:
                return path

            neighbors = self.generate_grids(grid)
            for neighbor in neighbors:
                if tuple(map(tuple, neighbor)) not in visited:
                    heapq.heappush(priority_queue, (self.evaluate_state(neighbor), neighbor, path + [neighbor]))
        return None

    def evaluate_state(self, state):
        # Fonction d'évaluation : retourne le nombre de tuiles mal placées
        nbre_unplaced_tiles = 0
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE):
                if state[i][j] != self.completed_grid[i][j]:
                    nbre_unplaced_tiles += 1
        return nbre_unplaced_tiles

    def evaluate_state2(self, state, depth):
        nbre_unplaced_tiles = 0
        for i in range(GAME_SIZE):
            for j in range(GAME_SIZE):
                if state[i][j] != self.completed_grid[i][j]:
                    nbre_unplaced_tiles += 1
        return nbre_unplaced_tiles + depth

    def generate_grids(self, grid):
        neighbors = []
        empty_x, empty_y = self.find_empty_tile(grid)
        directions = [(empty_x + 1, empty_y), (empty_x - 1, empty_y), (empty_x, empty_y + 1), (empty_x, empty_y - 1)]
        for next_x, next_y in directions:
            if 0 <= next_x < GAME_SIZE and 0 <= next_y < GAME_SIZE:
                new_grid = [row[:] for row in grid]
                new_grid[empty_x][empty_y], new_grid[next_x][next_y] = new_grid[next_x][next_y], new_grid[empty_x][
                    empty_y]
                neighbors.append(new_grid)
        return neighbors


# Création des boutons
shuffle_button = Button(Shuffle_Button, (WIDTH - 150, HEIGHT // 2 - 50))
reset_button = Button(Reset_Button, (WIDTH - 150, HEIGHT // 5 + 450 ))
bfs_button = Button(BFS_Button, (150, HEIGHT // 2 - 50))
a_etoile_button = Button(A_etoile, (150, HEIGHT // 5 + 450))


def draw_buttons():
    shuffle_button.draw(screen)
    reset_button.draw(screen)
    bfs_button.draw(screen)
    a_etoile_button.draw(screen)


def draw_all():
    screen.fill(NEON)
    game.draw_tiles()
    game.draw_grid()
    draw_buttons()


# Boucle de jeu
game = Game()
game.shuffle()
moves = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            mouse_pos = (mouse_x, mouse_y)
            clicked_x, clicked_y = game.clicked_tile(mouse_x, mouse_y)
            if shuffle_button.is_clicked(mouse_pos):
                moves = 0
                game.shuffle()
            elif reset_button.is_clicked(mouse_pos):
                moves = 0
                game.reset()
            elif bfs_button.is_clicked(mouse_pos):
                win_path = game.bfs_solution()
                if win_path:
                    for i, grid_step in enumerate(win_path):
                        game.player_grid = grid_step
                        moves = i + 1
                        print("move n°", moves)
                        for row in grid_step:
                            print(row)
                        draw_all()
                        pygame.display.update()
                        pygame.time.wait(500)
                else:
                    print("Aucune solution trouvée.")
            elif a_etoile_button.is_clicked(mouse_pos):
                win_path = game.a_etoile_solution()
                if win_path:
                    for i, grid_step in enumerate(win_path):
                        game.player_grid = grid_step
                        moves = i + 1
                        print("move n°", moves)
                        for row in grid_step:
                            print(row)
                        draw_all()
                        pygame.display.update()
                        pygame.time.wait(500)
                else:
                    print("Aucune solution trouvée.")
            else:
                if pygame.mouse.get_pressed()[0] == 1 and not game.win():
                    game.handle_move(clicked_x, clicked_y)
                    moves += 1
    if game.win():
        screen.fill(NEON)
        shuffle_button.draw(screen)
        reset_button.draw(screen)
        screen.blit(win_message, win_message_rect)
        moves_text = font.render(f"Moves: {moves}", True, BLACK)
        moves_rect = moves_text.get_rect(midtop=(WIDTH // 2, HEIGHT // 2))
        screen.blit(moves_text, moves_rect)

    else:
        draw_all()
    game.clock.tick(FPS)
    pygame.display.update()
