import pygame
import sys

class Controller:
    def __init__(self, model, view, config, item_manager):
        self.model = model
        self.view = view
        self.config = config
        self.clock = pygame.time.Clock()
        self.running = True
        self.item_manager = item_manager

    def movement_handler(self, dt):
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
            self.model.move(direction_x, direction_y, sprint, dt)

    def inventory_handler(self, event):
        if event.type == pygame.MOUSEWHEEL:
            self.model.inventory.scroll(-event.y)

        if event.type == pygame.KEYDOWN:
            inventory_key_map = {
                pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
                pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5,
                pygame.K_7: 6, pygame.K_8: 7, pygame.K_9: 8
            }
            if event.key in inventory_key_map:
                self.model.inventory.select_slot(inventory_key_map[event.key])

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.model.item_picker(self.item_manager)
                if event.key == pygame.K_q:
                    self.model.item_dropper(self.item_manager)


    def main_loop(self):

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.inventory_handler(event)

            dt = self.clock.tick(self.config.fps) / 1000.0

            self.movement_handler(dt)
            self.view.draw_world(self.model, self.item_manager)

            pygame.display.set_caption(f"GTA Łódź - FPS: {int(self.clock.get_fps())}")

        pygame.quit()
        sys.exit()