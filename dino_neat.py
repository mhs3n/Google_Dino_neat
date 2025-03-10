import pygame
import os
import random
import neat
import math
import pickle

pygame.init()

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1300
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus3.png"))]
BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))
BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))

class Dinosaur:
    X_POS = 80
    Y_POS = 310
    Y_POS_DUCK = 340
    JUMP_VEL = 8.5
    MAX_JUMP_HEIGHT = 100

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING
        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False
        self.step_index = 0
        self.jump_vel = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, action):
        if self.dino_duck:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if action == 1 and not self.dino_jump and self.dino_rect.y >= self.Y_POS - 10 and self.dino_rect.y > self.MAX_JUMP_HEIGHT:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif action == 2 and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif not self.dino_jump:
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 5]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
            if self.dino_rect.y >= self.Y_POS:
                self.dino_rect.y = self.Y_POS
                self.dino_jump = False
                self.jump_vel = self.JUMP_VEL
            elif self.dino_rect.y < self.MAX_JUMP_HEIGHT:
                self.jump_vel = -self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.x, self.y))

class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop(0)

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325

class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 300

class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)
        self.rect.y = 250
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 9:
            self.index = 0
        SCREEN.blit(self.image[self.index // 5], self.rect)
        self.index += 1

# Global game variables
game_speed = 20
x_pos_bg = 0
y_pos_bg = 380
points = 0
obstacles = []
generation = 0
best_high_score = 0
saved_10000 = False

def get_game_state(player, obstacles):
    if not obstacles:
        return [game_speed, 1000, 0, 0, player.dino_rect.y, player.jump_vel, 1000, 0]
    nearest_obstacle = min(obstacles, key=lambda o: o.rect.x if o.rect.x > player.dino_rect.x else float('inf'))
    distance = nearest_obstacle.rect.x - player.dino_rect.x
    obs_type = 1 if isinstance(nearest_obstacle, Bird) else 0
    next_distance = 1000
    next_type = 0
    if len(obstacles) > 1:
        next_obstacle = min([o for o in obstacles if o.rect.x > nearest_obstacle.rect.x], key=lambda o: o.rect.x, default=None)
        if next_obstacle:
            next_distance = next_obstacle.rect.x - player.dino_rect.x
            next_type = 1 if isinstance(next_obstacle, Bird) else 0
    return [game_speed, distance, obs_type, nearest_obstacle.rect.y, player.dino_rect.y, player.jump_vel, next_distance, next_type]

def draw_network(genome, screen, x=700, y=50, width=400, height=200):
    font = pygame.font.Font(None, 24)
    node_radius = 12
    input_nodes = [-8, -7, -6, -5, -4, -3, -2, -1]
    output_nodes = [0, 1, 2]
    hidden_nodes = [node_id for node_id in genome.nodes.keys() if node_id not in input_nodes and node_id not in output_nodes]

    input_x = x
    hidden_x = x + width // 3
    output_x = x + (2 * width // 3)

    max_nodes = max(len(input_nodes), len(hidden_nodes), len(output_nodes))
    if max_nodes > 0:
        v_spacing = min(40, height // max_nodes)

    # Draw input nodes
    input_labels = ["Speed", "Dist", "Type", "ObsY", "DinoY", "JumpVel", "NextDist", "NextType"]
    for i, node_id in enumerate(input_nodes):
        pos_y = y + i * v_spacing
        pygame.draw.circle(screen, (180, 180, 180), (input_x, pos_y), node_radius + 2)
        pygame.draw.circle(screen, (220, 220, 220), (input_x, pos_y), node_radius)
        label = font.render(input_labels[i], True, (0, 0, 0))
        screen.blit(label, (input_x - 50, pos_y - 10))

    # Draw hidden nodes
    for i, node_id in enumerate(hidden_nodes):
        pos_y = y + i * v_spacing
        pygame.draw.circle(screen, (180, 180, 180), (hidden_x, pos_y), node_radius + 2)
        pygame.draw.circle(screen, (220, 220, 220), (hidden_x, pos_y), node_radius)
        label = font.render(f"H{node_id}", True, (0, 0, 0))
        screen.blit(label, (hidden_x - 20, pos_y - 10))

    # Draw output nodes
    output_labels = ["Nothing", "Jump", "Duck"]
    for i, node_id in enumerate(output_nodes):
        pos_y = y + i * v_spacing
        pygame.draw.circle(screen, (180, 180, 180), (output_x, pos_y), node_radius + 2)
        pygame.draw.circle(screen, (220, 220, 220), (output_x, pos_y), node_radius)
        label = font.render(output_labels[i], True, (0, 0, 0))
        screen.blit(label, (output_x + 15, pos_y - 10))

    # Store node positions
    node_positions = {}
    for i, node_id in enumerate(input_nodes):
        node_positions[node_id] = (input_x, y + i * v_spacing)
    for i, node_id in enumerate(hidden_nodes):
        node_positions[node_id] = (hidden_x, y + i * v_spacing)
    for i, node_id in enumerate(output_nodes):
        node_positions[node_id] = (output_x, y + i * v_spacing)

    # Draw connections with color gradient
    for (in_node, out_node), conn in genome.connections.items():
        if conn.enabled and in_node in node_positions and out_node in node_positions:
            in_x, in_y = node_positions[in_node]
            out_x, out_y = node_positions[out_node]
            weight = abs(conn.weight)
            thickness = min(5, max(1, int(weight * 2)))
            red_value = max(139, int(255 - (weight * 50)))
            green_blue_value = max(0, int(150 - (weight * 75)))
            color = (red_value, green_blue_value, green_blue_value)
            pygame.draw.line(screen, color, (in_x, in_y), (out_x, out_y))


def eval_genomes(genomes, config):
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, generation, best_high_score, saved_10000

    game_speed = 20
    x_pos_bg = 0
    y_pos_bg = 380
    points = 0
    obstacles.clear()

    nets = []
    dinos = []
    ge = []

    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        dinos.append(Dinosaur())
        ge.append(genome)
        hidden_nodes = [node_id for node_id in genome.nodes.keys() if node_id not in [-8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2]]
       

    clock = pygame.time.Clock()
    cloud = Cloud()
    font = pygame.font.Font('freesansbold.ttf', 20)
    best_genome = ge[0]
    running = True

    while running and len(dinos) > 0:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        SCREEN.fill((255, 255, 255))

        if len(obstacles) == 0:
            rand = random.randint(0, 2)
            if rand == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif rand == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif rand == 2:
                obstacles.append(Bird(BIRD))

        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            x_pos_bg = 0
        x_pos_bg -= game_speed

        cloud.draw(SCREEN)
        cloud.update()

        best_fitness = -float('inf')
        for i, dino in enumerate(dinos):
            state = get_game_state(dino, obstacles)
            output = nets[i].activate(state)
            action = output.index(max(output))
            dino.update(action)
            dino.draw(SCREEN)
            ge[i].fitness += 0.5
            if ge[i].fitness > best_fitness:
                best_fitness = ge[i].fitness
                best_genome = ge[i]

        for obstacle in obstacles[:]:
            obstacle.draw(SCREEN)
            obstacle.update()
            i = 0
            while i < len(dinos):
                if dinos[i].dino_rect.colliderect(obstacle.rect):
                    ge[i].fitness -= 10
                    dinos.pop(i)
                    nets.pop(i)
                    ge.pop(i)
                else:
                    i += 1

        points += 1
        if points % 100 == 0:
            game_speed += 1
        for genome in ge:
            genome.fitness += points / 100.0

        if points > best_high_score:
            best_high_score = points

        if points >= 10000 and not saved_10000:
            with open('best_genome_10000_points.pkl', 'wb') as f:
                pickle.dump(best_genome, f)
            print(f"Saved genome with {points} points to 'best_genome_10000_points.pkl'")
            saved_10000 = True

        text = font.render(f"Points: {points}", True, (0, 0, 0))
        SCREEN.blit(text, (15, 20))
        gen_text = font.render(f"Generation: {generation}", True, (0, 0, 0))
        SCREEN.blit(gen_text, (15, 40))
        alive_text = font.render(f"Dinos Alive: {len(dinos)}", True, (0, 0, 0))
        SCREEN.blit(alive_text, (15, 60))
        high_score_text = font.render(f"Best High Score: {best_high_score}", True, (0, 0, 0))
        SCREEN.blit(high_score_text, (15, 80))

        draw_network(best_genome, SCREEN)

        clock.tick(30)
        pygame.display.update()

    generation += 1
    # No return statement; NEAT handles population creation

def run_game(config_file, max_generations=300):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes, max_generations)

    print(f"\nBest genome:\n{winner}")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        pygame.display.update()

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run_game(config_path)