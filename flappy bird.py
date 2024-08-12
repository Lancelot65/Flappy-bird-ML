import pygame
import random

pygame.init()
pygame.font.init()

font = pygame.font.SysFont("comicsansms", 20)

class Obstacle:
    def __init__(self, surface, seed, hauteur: int=140) -> None:
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

class GestionObstacle:
    def __init__(self, surface):
        self.list_obstacles = []
        self.counter = 50

        self.surface = surface

    def init_seed(self):
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
        if len(self.list_obstacles) > 0 and self.list_obstacles[0].rect_up.x < -50:
            self.list_obstacles.pop(0)

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

class Game:
    def __init__(self):
        self.window = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()

        self.gestion_obstacles = GestionObstacle(self.window)
        self.bird = Bird(self.window)

        self.next_mur = None
        self.copie = None

    def loop(self):
        loop_ = True
        self.POINT = 0

        self.gestion_obstacles.init_seed()

        while self.bird.on_life:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    loop_ = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
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

    def quit(self):
        pygame.quit()
    
    def update(self):
        self.next_obstacle()
        self.collision()
        self.check_point()

    def next_obstacle(self):
        for mur in self.gestion_obstacles.list_obstacles:
            if mur.rect_up.x + mur.rect_up.width + 5 > self.bird.rect.x:
                self.next_mur = mur
                if self.copie is None:
                    self.copie = self.next_mur
                break
    
    def check_point(self):
        if self.copie is not None:
            if self.copie != self.next_mur:
                self.copie = self.next_mur
                self.POINT +=1
    
    def draw_stat(self):
        text = font.render(str(self.POINT), True,(255, 255, 255))
        self.window.blit(text, (20, 20))
    
    def collision(self):
        if self.next_mur is not None:
            if self.bird.rect.colliderect(self.next_mur.rect_up) or self.bird.rect.colliderect(self.next_mur.rect_down):
                self.bird.dead()

game = Game()
game.loop()
game.quit()