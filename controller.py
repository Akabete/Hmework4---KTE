import pygame
import sys

class Controller:
    def __init__(self, model, view, config):
        self.model = model
        self.view = view
        self.config = config
        self.clock = pygame.time.Clock()
        self.running = True

    def movement_handler(self):
        keys = pygame.key.get_pressed()
        direction_x = 0
        direction_y = 0
        sprint = 0

        if keys[pygame.K_w]:
            direction_y = -1
        if keys[pygame.K_s]:
            direction_y = 1
        if keys[pygame.K_a]:
            direction_x = -1
        if keys[pygame.K_d]:
            direction_x = 1
        if keys[pygame.K_LSHIFT]:
            sprint = 1

        if direction_x != 0 or direction_y != 0:
            self.model.move(direction_x, direction_y, sprint)

    def main_loop(self):

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.movement_handler()
            self.view.draw_world(self.model)
            self.clock.tick(self.config.fps)

        pygame.quit()
        sys.exit()