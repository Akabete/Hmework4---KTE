import pygame
import sys

import model


class Controller:
    def __init__(self, model, view, config, item_manager, enemy_manager):
        self.model = model
        self.view = view
        self.config = config
        self.clock = pygame.time.Clock()
        self.running = True
        self.item_manager = item_manager
        self.enemy_manager = enemy_manager

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

    def use_handler(self):
        click = pygame.mouse.get_pressed()
        if click[0] == 1:
            inventory = self.model.inventory
            active_item = inventory.slots[inventory.selected_index]

            if active_item is not None:
                current_time = pygame.time.get_ticks()

                if current_time - active_item.last_use_time > active_item.use_speed:
                    active_item.last_use_time = current_time


    def main_loop(self):

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.inventory_handler(event)

            dt = self.clock.tick(self.config.fps) / 1000.0

            for enemy in self.enemy_manager.enemies_spawned:
                enemy.random_movement(dt, self.model)

            self.movement_handler(dt)
            self.use_handler()
            self.view.draw_world(self.model, self.item_manager, self.enemy_manager)

            pygame.display.set_caption(f"GTA Łódź - FPS: {int(self.clock.get_fps())}")

        pygame.quit()
        sys.exit()