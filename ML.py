import numpy as np
from neuron import perceptron_mutation
import pygame
from math import sqrt
import sys

import pygame
import random

pygame.init()
pygame.font.init()

font = pygame.font.SysFont("comicsansms", 20)

class Obstacle:
    def __init__(self, surface, seed, hauteur: int = 120) -> None:
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
        self.list_obstacles = [obstacle for obstacle in self.list_obstacles if obstacle.rect_up.x >= -50]

    def next_obstacle(self, bird_rect):
        for obstacle in self.list_obstacles:
            if obstacle.rect_up.x + obstacle.rect_up.width + 5 > bird_rect.x:
                return obstacle
        return None

class Bird:

    def __init__(self, surface, game):
        self.width_bird = 30
        self.color = pygame.Color(255, 250, 80)
        x, y = surface.get_width() / 2 - self.width_bird / 2, surface.get_height() / 2 - self.width_bird / 2
        self.rect = pygame.Rect(x, y, self.width_bird, self.width_bird)

        self.v_chute = 4
        self.gravite = 1
        self.jump_height = 12
        self.surface = surface
        self.on_life = True

        self.model = perceptron_mutation(2)
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

    def calcul(self):
        if self.game.next_mur is None:
            return 0
        distance_sol = self.surface.get_height() - self.rect.y
        distance_haut_gauche = Bird.distance_two_tuple(self.game.next_mur.rect_up.bottomleft, self.rect.center)
        distance_bas_gauche = Bird.distance_two_tuple(self.game.next_mur.rect_down.topleft, self.rect.center)
        return self.model.activation(self.model.pre_activation(np.array([distance_haut_gauche, distance_bas_gauche]))) #self.v_chute, distance_sol

    @staticmethod
    def distance_two_tuple(tuple1, tuple2):
        diff_x = tuple1[0] - tuple2[0]
        diff_y = tuple1[1] - tuple2[1]

        total = sqrt(diff_x**2 + diff_y**2)

        if tuple1[1] - tuple2[1] < 0:
            total = -total

        return total
    
    def mutation(self, new_weight):
        self.model.update_waights(new_weight)
    
    def action(self):
        if self.calcul() >= 0.5: self.jump()
    

class AllBird:
    def __init__(self, surface, game) -> None:
        self.surface = surface
        self.game = game

        self.nbr_bird = 200
        self.liste_bird = [Bird(self.surface, self.game) for _ in range(self.nbr_bird)]
    
        self.copie = None
        self.best = None

        self.never_create = True

    def draw(self):
        for bird in self.liste_bird:
            bird.draw()
    
    def update(self):
        for bird in self.liste_bird:
            bird.update()

        self.liste_bird = [instance for instance in self.liste_bird if instance.on_life != 0]

        if len(self.liste_bird) == 0:
            self.best = self.copie[0] if self.copie else None
            self.game.loop_ = False

        if len(self.liste_bird) != 0:
            self.copie = self.liste_bird.copy()
    
    def mutation(self):
        if self.best is None:
            return
        
        # if self.never_create:
        #     self.never_create = False
        #     self.liste_bird = [Bird(self.surface, self.game) for i in range(self.nbr_bird)]

        self.liste_bird = [Bird(self.surface, self.game) for i in range(self.nbr_bird)]
        
        for bird in self.liste_bird:
            bird.mutation(self.best.model.weights)

class CollisionManager:
    @staticmethod
    def check_collision(liste_bird, obstacle):
        for bird in liste_bird:
            bird_rect = bird.rect
            for rect in obstacle.get_rects():
                if bird_rect.colliderect(rect):
                    bird.dead()


class Game:
    def __init__(self):
        self.window = pygame.display.set_mode((640, 480))
        self.clock = pygame.time.Clock()
        self.gestion_obstacles = GestionObstacle(self.window)
        self.gestion_bird = AllBird(self.window, self)
        self.POINT = 0
        self.last_obstacle = None

        self.next_mur = None
        self.copie = None

    def loop(self):
        self.loop_ = True
        self.POINT = 0
        while self.loop_:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.loop_ = False
                    sys.exit("programme intérompu")
            
            self.gestion_obstacles.update()
            self.gestion_bird.update()
            self.update()

            self.window.fill(pygame.Color(0, 200, 255))
            self.gestion_obstacles.draw()
            self.gestion_bird.draw()
            self.draw_stat()
            pygame.display.flip()
            self.clock.tick(30)

    def update(self):
        self.next_obstacle()
        self.colision()
    
    def next_obstacle(self):
        if self.loop_:
            for mur in self.gestion_obstacles.list_obstacles:
                if mur.rect_up.x + mur.rect_up.width + 5 > self.gestion_bird.liste_bird[0].rect.x:
                    self.next_mur = mur
                    if self.copie is None:
                        self.copie = self.next_mur
                    break

    def colision(self):
        if len(self.gestion_bird.liste_bird) != 0:
            next_obstacle = self.gestion_obstacles.next_obstacle(self.gestion_bird.liste_bird[0].rect)
            if next_obstacle:
                CollisionManager.check_collision(self.gestion_bird.liste_bird, next_obstacle)
                if next_obstacle != self.last_obstacle:
                    self.POINT += 1
                    self.last_obstacle = next_obstacle


    def check_point(self):
        if self.copie is not None:
            if self.copie != self.next_mur:
                self.copie = self.next_mur
                self.POINT += 1

    def draw_stat(self):
        text = font.render(str(self.POINT), True, (255, 255, 255))
        self.window.blit(text, (20, 20))
        text = font.render(str(len(self.gestion_bird.liste_bird)), True, (255, 255, 255))
        self.window.blit(text, (20, 45))

    def quit(self):
        pygame.quit()

class Train_model:
    def __init__(self, nbr_learn) -> None:
        self.nrb_learn = nbr_learn
        self.game = Game()
        self.train()

    def train(self):
        for i in range(self.nrb_learn):
            self.game.gestion_bird.mutation()
            self.game.gestion_obstacles.init_seed()
            if self.game.loop():
                print("programme intérrompu")
                return 

            if self.game.gestion_bird.best is not None:
                print("parametre : " + str(self.game.gestion_bird.best.model.weights))
                print(f"POINT : {self.game.POINT}")
            else:
                print("Aucun oiseau selectionné comme meilleur (erreur dans le code)")
        self.game.quit()
        print(self.game.gestion_bird.best.model.weights)

Train_model(20)