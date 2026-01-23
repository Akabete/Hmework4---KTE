import pygame
import math
import sys

import model


class Controller:
    def __init__(self, model, view, config, item_manager, enemy_manager, projectile_manager, cars_manager):
        self.model = model
        self.view = view
        self.config = config
        self.clock = pygame.time.Clock()
        self.running = True
        self.item_manager = item_manager
        self.enemy_manager = enemy_manager
        self.projectile_manager = projectile_manager
        self.cars_manager = cars_manager

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
            if self.model.current_vehicle is None:
                self.model.move(direction_x, direction_y, sprint, dt)
            else:
                self.model.current_vehicle.drive(direction_x, direction_y, dt)
                self.model.rect.center = self.model.current_vehicle.rect.center
                self.model.position_x = self.model.current_vehicle.rect.centerx
                self.model.position_y = self.model.current_vehicle.rect.centery

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

                    camera_x = self.model.rect.centerx - (self.config.screen_size[0] / 2)
                    camera_y = self.model.rect.centery - (self.config.screen_size[1] / 2)

                    if camera_x < 0:
                        camera_x = 0
                    elif camera_x > self.config.map_size[0] - self.config.screen_size[0]:
                        camera_x = self.config.map_size[0] - self.config.screen_size[0]
                    if camera_y < 0:
                        camera_y = 0
                    elif camera_y > self.config.map_size[1] - self.config.screen_size[1]:
                        camera_y = self.config.map_size[1] - self.config.screen_size[1]

                    mouse_position_x, mouse_position_y = pygame.mouse.get_pos()
                    mouse_position_x += camera_x
                    mouse_position_y += camera_y

                    position_difference_x = mouse_position_x - self.model.rect.centerx
                    position_difference_y = mouse_position_y - self.model.rect.centery

                    distance_travelled = math.sqrt( pow(position_difference_x, 2) + pow(position_difference_y, 2) )

                    if distance_travelled > 0:
                        direction_x = position_difference_x / distance_travelled
                        direction_y = position_difference_y / distance_travelled

                        projectile = model.Projectile(self.config, self.model.rect.centerx, self.model.rect.centery,
                                                     direction_x, direction_y, active_item.damage, self.config.weapon_bullet_speed, active_item.distance, self.config.projectile_texture)
                        self.projectile_manager.add_projectile(projectile)


    def vehicle_handler(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                for vehicle in self.cars_manager.cars_on_map:
                    if self.model.rect.colliderect(vehicle.rect):
                        if vehicle.rect.width == self.config.vehicle_hitbox_small[0]:
                            self.model.current_vehicle = vehicle
                            vehicle.position_x = vehicle.rect.x
                            vehicle.position_y = vehicle.rect.y

                            self.model.rect.center = vehicle.rect.center


    def main_loop(self):

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                self.inventory_handler(event)
                self.vehicle_handler(event)

            dt = self.clock.tick(self.config.fps) / 1000.0

            for enemy in self.enemy_manager.enemies_spawned:
                enemy.random_movement(dt, self.model)


            self.movement_handler(dt)
            self.use_handler()
            self.projectile_manager.move_projectiles(dt, self.enemy_manager, self.item_manager)
            self.enemy_manager.spawn_enemies()
            self.enemy_manager.replace_dead_enemies()
            self.cars_manager.spawn_cars()
            self.view.draw_world(self.model, self.item_manager, self.enemy_manager, self.cars_manager)

            pygame.display.set_caption(f"GTA Łódź - FPS: {int(self.clock.get_fps())}")

        pygame.quit()
        sys.exit()