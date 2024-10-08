import pygame
import random

pygame.init()
pygame.font.init()

font = pygame.font.SysFont("comicsansms", 20)

class Obstacle:
    def __init__(self, surface, seed, hauteur: int = 140) -> None:
        self.surface = surface
        height = surface.get_height()
        self.init_x = surface.get_width() + 50

        self.height_up = seed.randint(50, height - 40 - hauteur)
        self.height_down = height - self.height_up - hauteur

        self.rect_up = pygame.Rect(self.init_x, 0, 50, self.height_up)
        self.rect_down = pygame.Rect(self.init_x, height - self.height_down, 50, self.height_down)

        self.color = pygame.Color(255, 0, 0)
        self.speed = 5

    def draw(self):
        pygame.draw.rect(self.surface, self.color, self.rect_up)
        pygame.draw.rect(self.surface, self.color, self.rect_down)
    
    def update(self):
        self.rect_up.x -= self.speed
        self.rect_down.x -= self.speed

    def get_rects(self):
        return [self.rect_up, self.rect_down]

class GestionObstacle:
    def __init__(self, surface):
        self.list_obstacles = []
        self.counter = 50
        self.surface = surface
        self.seed = random.Random(0)

    def update(self):
        for obstacle in self.list_obstacles:
            obstacle.update()
        self.counter += 1
        if self.counter > 45:
            self.counter = 0
            self.list_obstacles.append(Obstacle(self.surface, self.seed))
        self.clean_obstacles()
    
    def draw(self):
        for obstacle in self.list_obstacles:
            obstacle.draw()
    
    def clean_obstacles(self):
        self.list_obstacles = [obstacle for obstacle in self.list_obstacles if obstacle.rect_up.x >= -50]

    def next_obstacle(self, bird_rect):
        for obstacle in self.list_obstacles:
            if obstacle.rect_up.x + obstacle.rect_up.width + 5 > bird_rect.x:
                return obstacle
        return None

class Bird:
    def __init__(self, surface):
        self.width_bird = 30
        self.color = pygame.Color(255, 250, 80)
        x, y = surface.get_width() / 2 - self.width_bird / 2, surface.get_height() / 2 - self.width_bird / 2
        self.rect = pygame.Rect(x, y, self.width_bird, self.width_bird)

        self.v_chute = 4
        self.gravite = 1
        self.jump_height = 12
        self.surface = surface
        self.on_life = True

    def update(self):
        self.v_chute += self.gravite
        self.rect.y += self.v_chute
        self.check_limit()
    
    def check_limit(self):
        if self.rect.y + self.width_bird - 20 > self.surface.get_height() or self.rect.y - self.width_bird + 20 < 0:
            self.on_life = False
    
    def draw(self):
        pygame.draw.rect(self.surface, self.color, self.rect)

    def jump(self):
        self.v_chute = -self.jump_height
    
    def dead(self):
        self.on_life = False

class CollisionManager:
    @staticmethod
    def check_collision(bird, obstacle):
        bird_rect = bird.rect
        for rect in obstacle.get_rects():
            if bird_rect.colliderect(rect):
                bird.dead()

class Game:
    def __init__(self):
        self.window = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        self.gestion_obstacles = GestionObstacle(self.window)
        self.bird = Bird(self.window)
        self.POINT = 0
        self.last_obstacle = None

    def loop(self):
        self.POINT = 0
        while self.bird.on_life:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.bird.on_life = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    self.bird.jump()
            
            self.gestion_obstacles.update()
            self.bird.update()
            self.update()

            self.window.fill(pygame.Color(0, 200, 255))
            self.gestion_obstacles.draw()
            self.bird.draw()
            self.draw_stat()
            pygame.display.flip()
            self.clock.tick(30)

    def update(self):
        next_obstacle = self.gestion_obstacles.next_obstacle(self.bird.rect)
        if next_obstacle:
            CollisionManager.check_collision(self.bird, next_obstacle)
            if next_obstacle != self.last_obstacle:
                self.POINT += 1
                self.last_obstacle = next_obstacle

    def draw_stat(self):
        text = font.render(str(self.POINT), True, (255, 255, 255))
        self.window.blit(text, (20, 20))

    def quit(self):
        pygame.quit()

game = Game()
game.loop()
game.quit()