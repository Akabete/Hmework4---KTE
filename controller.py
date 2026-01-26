import pygame
import math
import sys, os

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
        self.highlithed_button = 0
        self.menu_buttons = []

        for i, text in enumerate(self.config.menu_options):
            button_x = (self.config.display["screen_size"][0] / 2) - (self.config.menu_buttons["width"] / 2)
            button_y = self.config.menu_buttons["menu_first_y"] + (i *
                    (self.config.menu_buttons["height"] + self.config.menu_buttons["padding"]))

            button_rect = pygame.Rect(button_x, button_y,
                        self.config.menu_buttons["width"], self.config.menu_buttons["height"])

            self.menu_buttons.append({
                "text": text,
                "rect": button_rect
            })
            pass


    def _get_mouse_position(self):
        screen_x, screen_y = pygame.mouse.get_pos()
        camera_rect = self.view.get_camera_rect(self.model.rect)

        world_x = screen_x + camera_rect.x
        world_y = screen_y + camera_rect.y

        return world_x, world_y

    @staticmethod
    def _get_key_input():
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

        return direction_x, direction_y, sprint


    def movement_handler(self, dt):
        direction_x, direction_y, sprint = self._get_key_input()

        if self.model.current_vehicle is None:
            self.model.move(direction_x, direction_y, sprint, dt)
        else:
            self.model.current_vehicle.drive(direction_x, direction_y, dt)
            self.model.sync_with_vehicle()

    def inventory_handler(self, event):
        if event.type == pygame.MOUSEWHEEL:

            self.model.inventory.scroll(-event.y)
        if event.type == pygame.KEYDOWN:
            key_map = self.config.inventory_key_map

            if event.key in key_map:
                self.model.inventory.select_slot(key_map[event.key])

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    self.model.item_picker(self.item_manager)
                if event.key == pygame.K_q:
                    self.model.item_dropper(self.item_manager)


    @staticmethod
    def _is_item_ready(item):
        current_time = pygame.time.get_ticks()
        if current_time - item.last_use_time > item.use_speed:
            return True
        return False

    @staticmethod
    def calculate_vector(start_x, start_y, target_x, target_y):
        difference_x = target_x - start_x
        difference_y = target_y - start_y

        distance = math.sqrt(difference_x**2 + difference_y**2)

        if distance > 0:
            dx = difference_x / distance
            dy = difference_y / distance
            return dx, dy
        return 0, 0


    def _spawn_projectile(self, direction_x, direction_y, item):
        item.last_use_time = pygame.time.get_ticks()
        projectile = model.Projectile(self.config, self.model.rect.centerx,
                    self.model.rect.centery, direction_x, direction_y, item.damage,
                    self.config.combat["bullet_speed"], item.projectile_range,
                    self.config.combat["projectile_texture"])
        self.projectile_manager.add_projectile(projectile)


    def use_handler(self):
        click = pygame.mouse.get_pressed()
        mouse_x, mouse_y = self._get_mouse_position()
        direction_x, direction_y = self.calculate_vector(
            self.model.rect.centerx, self.model.rect.centery, mouse_x, mouse_y)
        if click[0] == 1:
            inventory = self.model.inventory
            active_item = inventory.slots[inventory.selected_index]

            if active_item is not None and self._is_item_ready(active_item):
                self._spawn_projectile(direction_x, direction_y, active_item)


    def vehicle_handler(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if self.model.current_vehicle is not None:
                self.model.x = self.model.rect.centerx
                self.model.visible = True
                self.model.current_vehicle = None
                return

            for vehicle in self.cars_manager.cars_on_map:
                if self.model.rect.colliderect(vehicle.rect):
                    self.model.current_vehicle = vehicle
                    vehicle.position_x = vehicle.rect.x
                    vehicle.position_y = vehicle.rect.y
                    self.model.rect.center = vehicle.rect.center

                    self.model.current_vehicle = vehicle
                    self.model.visible = not vehicle.hiding
                    break

    @staticmethod
    def open_settings():
        file_path = "settings.py"

        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            print("File not found")


    def reset_game(self):
        self.config.state = "PLAYING"

        self.model.hp = self.config.player["hp"]
        self.model.position_x, self.model.position_y = self.config.player["spawn_location"]
        self.model.rect.topleft = (self.model.position_x, self.model.position_y)
        self.model.inventory = model.Inventory()

        self.enemy_manager.reset_manager()
        self.cars_manager.reset_manager()
        self.model.current_vehicle = None
        self.item_manager.reset_manager()
        self.projectile_manager.bullets_on_map.clear()

    def main_loop(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:
                    if self.config.state == "START" or self.config.state == "GAME OVER":
                        if event.key == pygame.K_ESCAPE:
                            self.running = False
                        elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                            self.highlithed_button = (self.highlithed_button + 1) % len(self.menu_buttons)
                        elif event.key == pygame.K_UP or event.key == pygame.K_w:
                            self.highlithed_button = (self.highlithed_button - 1) % len(self.menu_buttons)
                        elif event.key == pygame.K_RETURN:
                            if self.highlithed_button == 0: self.reset_game()
                            elif self.highlithed_button == 1: self.open_settings()
                            else: self.running = False

                    if self.config.state == "PLAYING":
                        if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                            self.config.state = "PAUSED"
                    elif self.config.state == "PAUSED":
                        if event.key == pygame.K_p: self.config.state = "PLAYING"
                        if event.key == pygame.K_ESCAPE: self.config.state = "START"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (self.config.state == "START" or self.config.state == "GAME OVER") and event.button == 1:
                        for i, button in enumerate(self.menu_buttons):
                            if button["rect"].collidepoint(event.pos):
                                if i == 0: self.reset_game()
                                elif i == 1: self.open_settings()
                                else: self.running = False

                if self.config.state == "PLAYING":
                    self.inventory_handler(event)
                    self.vehicle_handler(event)


            if self.config.state == "START" or self.config.state == "GAME OVER":
                mouse_position = pygame.mouse.get_pos()
                for i, button in enumerate(self.menu_buttons):
                    if button["rect"].collidepoint(mouse_position):
                        self.highlithed_button = i

            dt = self.clock.tick(self.config.display["fps"]) / 1000.0

            if self.config.state == "PLAYING":
                if self.model.hp <= 0:
                    self.config.state = "GAME OVER"

                for enemy in self.enemy_manager.enemies_spawned:
                    enemy.think(self.model)
                    enemy.update(dt, self.model)
                self.movement_handler(dt)
                self.use_handler()
                self.projectile_manager.move_projectiles(dt, self.enemy_manager, self.item_manager)
                self.enemy_manager.spawn_enemies()
                self.enemy_manager.replace_dead_enemies()
                self.cars_manager.spawn_cars()
                self.view.draw_world(self.model, self.item_manager, self.enemy_manager)

            elif self.config.state == "START" or self.config.state == "GAME OVER":
                self.view.draw_menu(self.menu_buttons, self.highlithed_button)

            pygame.display.set_caption(f"Schmopp - FPS: {int(self.clock.get_fps())}")

        pygame.quit()
        sys.exit()