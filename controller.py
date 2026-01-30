import pygame
import math
import sys
import os

import model


class Controller:
    """
    Class responsible for controlling the game logic and handling user input.
    :attrib game_model: The model of the game.
    :attrib view: The view of the game.
    :attrib config: The configuration of the game.
    :attrib item_manager: The manager for items.
    :attrib enemy_manager: The manager for enemies.
    :attrib projectile_manager: The manager for projectiles.
    :attrib cars_manager: The manager for cars.
    """

    def __init__(
        self,
        game_model,
        view,
        config,
        item_manager,
        enemy_manager,
        projectile_manager,
        cars_manager,
    ):
        """
        Initializes the Controller class.
        :param game_model: The model of the game.
        :param view: The view of the game.
        :param config: The configuration of the game.
        :param item_manager: The manager for items.
        :param enemy_manager: The manager for enemies.
        :param projectile_manager: The manager for projectiles.
        :param cars_manager: The manager for cars.
        :return: None
        """
        self.model = game_model
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
            button_x = (self.config.display["screen_size"][0] / 2) - (
                self.config.menu_buttons["width"] / 2
            )
            button_y = self.config.menu_buttons["menu_first_y"] + (
                i
                * (
                    self.config.menu_buttons["height"]
                    + self.config.menu_buttons["padding"]
                )
            )

            button_rect = pygame.Rect(
                button_x,
                button_y,
                self.config.menu_buttons["width"],
                self.config.menu_buttons["height"],
            )

            self.menu_buttons.append({"text": text, "rect": button_rect})
            pass

    def _get_mouse_position(self):
        """
        Gets the current mouse position in the world coordinates.
        :return: tuple
        """
        screen_x, screen_y = pygame.mouse.get_pos()
        camera_rect = self.view.get_camera_rect(self.model.rect)

        world_x = screen_x + camera_rect.x
        world_y = screen_y + camera_rect.y

        return world_x, world_y

    @staticmethod
    def _get_key_input():
        """
        Gets the keyboard input for movement.
        :return: tuple
        """
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
        """
        Handles the movement of the player or vehicle.
        :param dt: The time passed since the last frame.
        :return: None
        """
        direction_x, direction_y, sprint = self._get_key_input()

        if self.model.current_vehicle is None:
            self.model.move(direction_x, direction_y, sprint, dt)
        else:
            self.model.current_vehicle.drive(direction_x, direction_y, dt)
            self.model.sync_with_vehicle()

    def inventory_handler(self, event):
        """
        Handles the inventory interactions based on user input.
        :param event: The pygame event.
        :return: None
        """
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
        """
        Checks if the item is ready to be used.
        :param item: The item to check.
        :return: bool
        """
        current_time = pygame.time.get_ticks()
        if current_time - item.last_use_time > item.use_speed:
            return True
        return False

    @staticmethod
    def calculate_vector(start_x, start_y, target_x, target_y):
        """
        Calculates the normalized vector between two points.
        :param start_x: Start X coordinate.
        :param start_y: Start Y coordinate.
        :param target_x: Target X coordinate.
        :param target_y: Target Y coordinate.
        :return: tuple
        """
        difference_x = target_x - start_x
        difference_y = target_y - start_y

        distance = math.sqrt(difference_x**2 + difference_y**2)

        if distance > 0:
            dx = difference_x / distance
            dy = difference_y / distance
            return dx, dy
        return 0, 0

    def _spawn_projectile(self, direction_x, direction_y, item):
        """
        Spawns a projectile in the specified direction.
        :param direction_x: X component of the direction vector.
        :param direction_y: Y component of the direction vector.
        :param item: The item used to spawn the projectile.
        :return: None
        """
        item.last_use_time = pygame.time.get_ticks()
        projectile = model.Projectile(
            self.config,
            self.model.rect.centerx,
            self.model.rect.centery,
            direction_x,
            direction_y,
            item.damage,
            self.config.combat["bullet_speed"],
            item.projectile_range,
            self.config.combat["projectile_texture"],
        )
        self.projectile_manager.add_projectile(projectile)

    def use_handler(self):
        """
        Handles the use of the currently active item.
        :return: None
        """
        click = pygame.mouse.get_pressed()
        mouse_x, mouse_y = self._get_mouse_position()
        direction_x, direction_y = self.calculate_vector(
            self.model.rect.centerx, self.model.rect.centery, mouse_x, mouse_y
        )
        if click[0] == 1:
            inventory = self.model.inventory
            active_item = inventory.slots[inventory.selected_index]

            if active_item is not None and self._is_item_ready(active_item):
                self._spawn_projectile(direction_x, direction_y, active_item)

    def vehicle_handler(self, event):
        """
        Handles entering and exiting vehicles.
        :param event: The pygame event.
        :return: None
        """
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
        """
        Opens the settings file.
        :return: None
        """
        file_path = "settings.py"

        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            print("File not found")

    def reset_game(self):
        """
        Resets the game state.
        :return: None
        """
        self.config.state = "PLAYING"
        self.config.current_score = 0

        self.model.hp = self.config.player["hp"]
        self.model.position_x, self.model.position_y = self.config.player[
            "spawn_location"
        ]
        self.model.rect.topleft = (self.model.position_x, self.model.position_y)
        self.model.inventory = model.Inventory()

        self.enemy_manager.reset_manager()
        self.cars_manager.reset_manager()
        self.model.current_vehicle = None
        self.item_manager.reset_manager()
        self.projectile_manager.bullets_on_map.clear()

    def _handle_events(self):
        """
        Handles all pygame events.
        :return: None
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.config.state in ["START", "GAME OVER"]:
                mouse_pos = pygame.mouse.get_pos()
                for i, button in enumerate(self.menu_buttons):
                    if button["rect"].collidepoint(mouse_pos):
                        self.highlithed_button = i

            if self.config.state == "START" or self.config.state == "GAME OVER":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.highlithed_button = (self.highlithed_button - 1) % len(
                            self.config.menu_options
                        )
                    if event.key == pygame.K_DOWN:
                        self.highlithed_button = (self.highlithed_button + 1) % len(
                            self.config.menu_options
                        )

                    if event.key == pygame.K_RETURN:
                        if self.highlithed_button == 0:
                            self.reset_game()
                        elif self.highlithed_button == 1:
                            self.open_settings()
                        elif self.highlithed_button == 2:
                            self.running = False

                if (
                    event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
                ):
                    if self.highlithed_button == 0:
                        self.reset_game()
                    elif self.highlithed_button == 1:
                        self.open_settings()
                    elif self.highlithed_button == 2:
                        self.running = False

            if self.config.state == "PLAYING":
                self.inventory_handler(event)
                self.vehicle_handler(event)

    def _update_logic(self, dt):
        """
        Updates the game logic.
        :param dt: The time passed since the last frame.
        :return: None
        """
        if self.config.state != "PLAYING":
            return

        if self.model.hp <= 0:
            self.config.state = "GAME OVER"
            if self.config.current_score > self.config.highscore:
                self.config.highscore = self.config.current_score
                self.config.save_high_score()

        for enemy in self.enemy_manager.enemies_spawned:
            enemy.think(self.model)
            enemy.update(dt, self.model)

        self.movement_handler(dt)
        self.use_handler()
        self.projectile_manager.move_projectiles(
            dt, self.enemy_manager, self.item_manager
        )

        self.enemy_manager.spawn_enemies()
        self.enemy_manager.replace_dead_enemies()
        self.cars_manager.spawn_cars()

    def _render(self):
        """
        Renders the game.
        :return: None
        """
        if self.config.state == "PLAYING":
            self.view.draw_world(self.model, self.item_manager, self.enemy_manager)
        elif self.config.state in ["START", "GAME OVER"]:
            self.view.draw_menu(self.menu_buttons, self.highlithed_button)

    def main_loop(self):
        """
        Main loop of the game.
        :return: None
        """
        while self.running:
            dt = self.clock.tick(self.config.display["fps"]) / 1000.0

            self._handle_events()
            self._update_logic(dt)
            self._render()

            pygame.display.set_caption(f"Schmopp - FPS: {int(self.clock.get_fps())}")

        pygame.quit()
        sys.exit()
