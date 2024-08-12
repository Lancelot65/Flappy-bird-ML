import pygame
import random
from math import sqrt

pygame.init()
pygame.font.init()

font = pygame.font.SysFont("comicsansms", 20)

class Obstacle:
    def __init__(self, surface, seed, hauteur: int=120) -> None:
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
        self.list_obstacles = []
        self.counter = 50

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
    def __init__(self, surface, game):
        self.width_bird = 30
        self.color = pygame.Color(255, 250, 80)

        x, y = surface.get_width() / 2 - self.width_bird / 2, surface.get_height() / 2 - self.width_bird / 2
        self.rect = pygame.Rect(x, y, self.width_bird, self.width_bird)

        self.v_chute = 4
        self.gravite = 1
        self.jump_height = 12
        self.on_life = True

        self.surface = surface

        self.parametre = [0.1, 1.3, -1, -0.3]
        self.bias = 0
        self.mutation_pourcentage = 0.3
        self.mutation_evolution = 0.3

        self.game = game

    def update(self):
        self.action()
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

    def first_assignation(self):
        for index, value in enumerate(self.parametre):
            self.parametre[index] = random.uniform(-self.mutation_evolution * 1000, self.mutation_evolution * 1000) / 1000
        self.bias = random.uniform(-self.mutation_evolution * 1000, self.mutation_evolution * 1000) / 1000

    def mutation(self, parametre, biais):
        for index, value in enumerate(parametre):
            if random.random() <= self.mutation_pourcentage:
                self.parametre[index] = value + random.uniform(-self.mutation_evolution * 1000, self.mutation_evolution * 1000) / 1000
            else:
                self.parametre[index] = value
        if random.random() <= self.mutation_pourcentage:
                self.bias = self.bias + random.uniform(-self.mutation_evolution * 1000, self.mutation_evolution * 1000) / 1000

    def calcul(self):
        if self.game.next_mur is None:
            return 0
        distance_sol = self.surface.get_height() - self.rect.y
        distance_haut_gauche = self.distance_two_tuple(self.game.next_mur.rect_up.bottomleft, self.rect.center)
        distance_bas_gauche  = self.distance_two_tuple(self.game.next_mur.rect_down.topleft, self.rect.center)
        return self.v_chute * self.parametre[0]  +  distance_sol * self.parametre[1]  +  distance_haut_gauche * self.parametre[2]  +  distance_bas_gauche * self.parametre[3]  +  self.bias

    def distance_two_tuple(self, tuple1, tuple2):
        diff_x = tuple1[0] - tuple2[0]
        diff_y = tuple1[1] - tuple2[1]

        total = sqrt(diff_x**2 + diff_y ** 2)

        if tuple1[1] - tuple2[1] < 0:
            total = -total

        return total

    def action(self):
        x = self.calcul()
        if x <= 0.5:
            self.jump()
        else:
            pass

class GestionBird:
    def __init__(self, surface, game):
        self.nbr_bird = 1000

        self.tout_mes_bird = [Bird(surface, game) for i in range(self.nbr_bird)]
        self.first_assignation()

        self.game = game
        self.surface = surface

    def first_assignation(self):
        for bird in self.tout_mes_bird:
            bird.first_assignation()
    
    def mutation(self):
        self.tout_mes_bird = [Bird(self.surface, self.game) for i in range(self.nbr_bird)]
        for bird in self.tout_mes_bird:
            bird.mutation(self.best.parametre, self.best.bias)
    
    def update(self):
        for bird in self.tout_mes_bird:
            bird.update()
        
        self.tout_mes_bird = [instance for instance in self.tout_mes_bird if instance.on_life != 0]
        
        if len(self.tout_mes_bird) == 0:
            self.best = self.copie[0]
            self.game.loop_ = False

        if len(self.tout_mes_bird) != 0:
            self.copie = self.tout_mes_bird
        
    def draw(self):
        for bird in self.tout_mes_bird:
            bird.draw()

class Game:
    def __init__(self, generation):
        self.window = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()

        self.gestion_obstacles = GestionObstacle(self.window)
        self.GestionBird = GestionBird(self.window, self)

        self.next_mur = None
        self.copie = None
        self.loop_ = True

        self.fps = 30
        
        self.generation = generation

    def loop(self):
        self.POINT = 0

        self.gestion_obstacles.init_seed()
        self.loop_ = True

        while self.loop_:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.loop_ = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.fps -= 5
                    elif event.key == pygame.K_p:
                        self.fps += 5
            
            self.gestion_obstacles.update()
            self.GestionBird.update()
            self.update()


            self.window.fill(pygame.Color(0, 200, 255))

            self.gestion_obstacles.draw()
            self.GestionBird.draw()
            self.draw_stat()

            pygame.display.flip()
            self.clock.tick(self.fps)        

    def quit(self):
        pygame.quit()
    
    def update(self):
        self.next_obstacle()
        self.collision()
        self.check_point()

    def next_obstacle(self):
        if self.loop_:
            for mur in self.gestion_obstacles.list_obstacles:
                if mur.rect_up.x + mur.rect_up.width + 5 > self.GestionBird.tout_mes_bird[0].rect.x:
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
        text = "Point : " + str(self.POINT)
        text = font.render(text, True,(255, 255, 255))
        self.window.blit(text, (20, 20))

        text = "Génération : " + str(self.generation)
        text = font.render(str(text), True,(255, 255, 255))
        self.window.blit(text, (20, 40))
    
        text = "bird en vie : " + str(len(self.GestionBird.tout_mes_bird))
        text = font.render(str(text), True,(255, 255, 255))
        self.window.blit(text, (20, 60))
    
    def collision(self):
        if self.next_mur is not None:
            for bird in self.GestionBird.tout_mes_bird:
                if bird.rect.colliderect(self.next_mur.rect_up) or bird.rect.colliderect(self.next_mur.rect_down):
                    bird.dead()


class Train_model:
    def __init__(self, nbr_learn) -> None:
        self.nrb_learn = nbr_learn - 1
        self.nbr_generation = 1
        self.game = Game(self.nbr_generation)

        self.game.loop()
        self.game.generation += 1

        print("parametre : " + str(self.game.GestionBird.best.parametre))
        print("bias : " + str(self.game.GestionBird.best.bias))
    
    def train(self):
        for i in range(self.nrb_learn):
            self.game.generation += 1
            self.game.GestionBird.mutation()
            self.game.gestion_obstacles.init_seed()
            self.game.loop()

            print("parametre : " + str(self.game.GestionBird.best.parametre))
            print("bias : " + str(self.game.GestionBird.best.bias))

model = Train_model(100)
model.train()