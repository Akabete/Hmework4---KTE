import pygame
import math
import sys
import os

import model


class Controller:
    """
    Handles the interaction between the game model, view, and various managers (e.g., item,
    enemy, projectile, and vehicle managers) to provide a seamless gameplay experience.

    This class is responsible for orchestrating the game's mechanics by managing inventory,
    handling events, controlling player/vehicle movement, managing combat behavior, and
    menu navigation. It serves as a central hub for connecting the core game logic with
    external systems such as input, rendering, and physics.

    :ivar model: Represents the game logic and state. Includes the player, vehicles, and their
        interactions.
    :type model: Any
    :ivar view: Handles the rendering and camera logic for displaying game visuals.
    :type view: Any
    :ivar config: Stores game configuration including settings for display, buttons,
        controls, etc.
    :type config: Any
    :ivar clock: Manages the game's timing and frame updates.
    :type clock: pygame.time.Clock
    :ivar running: Controls whether the game loop is active.
    :type running: Bool
    :ivar item_manager: Manager for handling item-related logic (e.g., spawning, pickup,
        dropping).
    :type item_manager: Any
    :ivar enemy_manager: Manager for handling enemy-related logic (e.g., spawning, movements,
        combat).
    :type enemy_manager: Any
    :ivar projectile_manager: Handles the lifecycle and behavior of projectiles (e.g.,
        bullets).
    :type projectile_manager: Any
    :ivar cars_manager: Handles vehicle management such as movement and interaction with the
        player.
    :type cars_manager: Any
    :ivar highlithed_button: Tracks the currently selected or hovered-over button in menus.
    :type highlithed_button: Int
    :ivar menu_buttons: Contains data about menu button positions, sizes, and labels for
        navigation.
    :type menu_buttons: List[dict]
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
        Calculates and returns the current mouse position in the world coordinates. This method
        adjusts the mouse position relative to the current camera view in the game world, ensuring
        the position corresponds to the environment within the game's logical space, rather than
        the screen coordinates.

        :return: A tuple containing the x and y coordinates of the mouse position in world space.
        :rtype: Tuple[int, int]
        """
        screen_x, screen_y = pygame.mouse.get_pos()
        camera_rect = self.view.get_camera_rect(self.model.rect)

        world_x = screen_x + camera_rect.x
        world_y = screen_y + camera_rect.y

        return world_x, world_y

    @staticmethod
    def _get_key_input():
        """
        Handles keyboard input to determine directional movement and sprinting.

        This static method captures the current state of specific keys using the
        `pygame.key.get_pressed()` function to detect player movements along the
        x and y axes, as well as the sprint action. The method computes the direction
        on each axis (x and y) based on the current key presses and determines whether
        the sprint input is active.

        :returns:
            A tuple containing the following:

            - Direction_x (int): -1 for left, 1 for right, 0 for no horizontal movement.
            - Direction_y (int): -1 for up, 1 for down, 0 for no vertical movement.
            - Sprint (int): 1 if sprinting is active (left shift pressed), 0 otherwise.
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
        Handles the movement input and delegates the movement logic based on whether the
        player is in a vehicle or on foot.

        If the player is on foot, their movement is managed directly. If the player is in
        a vehicle, the vehicle's movement logic is invoked and the player's position is
        synchronized with the vehicle.

        :param dt: The time delta since the last frame, used to ensure time-based movement.
                   Value is a float representing the elapsed time in seconds.
        :type dt: Float
        """
        direction_x, direction_y, sprint = self._get_key_input()

        if self.model.current_vehicle is None:
            self.model.move(direction_x, direction_y, sprint, dt)
        else:
            self.model.current_vehicle.drive(direction_x, direction_y, dt)
            self.model.sync_with_vehicle()

    def inventory_handler(self, event):
        """
        Handles user interactions with the inventory system, including scrolling, slot selection,
        item picking, and item dropping. Processes mouse wheel and keyboard input events
        to execute corresponding actions in the inventory model.

        :param event: The input event object representing user actions, such as mouse wheel
            movement or key presses.
        :type event: pygame.event.Event
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
        Determines whether the given item is ready for use based on its cooldown period.

        This static method computes the time difference between the current time and the
        item's last use time. If this difference exceeds the item's predefined use speed,
        the item is considered ready for use.

        :param item: The item to be checked for readiness. The item is expected to have
            `last_use_time` and `use_speed` attributes.
        :type item: Any
        :return: A boolean value indicating whether the item is ready for use.
        :rtype: Bool
        """
        current_time = pygame.time.get_ticks()
        if current_time - item.last_use_time > item.use_speed:
            return True
        return False

    @staticmethod
    def calculate_vector(start_x, start_y, target_x, target_y):
        """
        Calculate the normalized direction vector from a starting point to a target point.

        This static method computes the direction vector by taking the difference in
        coordinates between the starting point and the target point. It then normalizes
        the vector to ensure the magnitude is 1.0, unless the starting and target points
        are the same, in which case it returns (0, 0).

        :param start_x: The x-coordinate of the starting position.
        :type start_x: Float
        :param start_y: The y-coordinate of the starting position.
        :type start_y: Float
        :param target_x: The x-coordinate of the target position.
        :type target_x: Float
        :param target_y: The y-coordinate of the target position.
        :type target_y: Float
        :return: A tuple representing the normalized direction vector (dx, dy). If the
            distance between the points is zero, returns (0, 0).
        :rtype: Tuple[float, float]
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
        Spawns a projectile with a given direction and properties. Sets the last usage
        time for the item. Initializes a projectile based on the provided configuration
        and adds it to the projectile manager.

        :param direction_x: Horizontal direction of the projectile.
        :type direction_x: Float
        :param direction_y: Vertical direction of the projectile.
        :type direction_y: Float
        :param item: The item used to spawn the projectile, which contains properties
            such as damage, range, and last usage time.
        :type item: Object
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
        Handles user input and manages actions based on the input. Detects mouse clicks
        and determines the appropriate response by calculating direction vectors and
        interacting with the inventory to spawn projectiles when applicable.

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
        Handles the event of entering or exiting a vehicle in the game. This method checks
        for specific key-press events and interacts with the `self.model` object and
        vehicles available on the map. If the event matches the conditions for exiting a
        vehicle, it resets the player's position and vehicle association. If it matches
        conditions for entering a vehicle, it updates the player's position to match the
        vehicle and associates the player with the selected vehicle.

        :param event: The event object triggered during the game loop.
        :type event: pygame.event.Event
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
        Opens the settings file if it exists in the current directory. This method checks
        for the presence of a file named "settings.py" in the current working directory.
        If the file is found, it is opened. Otherwise, a message is displayed indicating
        that the file is not found.

        :return: None
        """
        file_path = "settings.py"

        if os.path.exists(file_path):
            os.startfile(file_path)
        else:
            print("File not found")

    def reset_game(self):
        """
        Resets the game to its initial state.

        This method reinitializes game configurations, player attributes, enemy managers,
        cars manager, item manager, and projectile manager to their default starting states.
        It ensures the game is set up and ready to begin or restart.

        :raises AttributeError: If any required attributes such as `state`, `current_score`,
            `player`, or `spawn_location` in `self.config` are missing or improperly defined.

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
        Handles all the game events based on the current game state and user inputs.

        This function processes a variety of game events such as quitting the game,
        navigating the menu, and handling interactions during gameplay. It updates
        the state of the game based on keyboard input, mouse position, and mouse
        clicks, while delegating specific event handling to other methods based on
        the gameplay context.

        :raises pygame.QUIT: When the quit event is triggered, sets the `running`
            status to `False` to exit the game loop.

        :raises pygame.KEYDOWN: Handles navigation between menu options, confirmation
            of menu choices with the Enter key, and other keyboard interaction.

        :raises pygame.MOUSEBUTTONDOWN: Handles mouse-based menu selection actions
            such as starting the game, opening settings, or quitting the game entirely.
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
        Updates the game logic for each frame during the 'PLAYING' state. This function controls the
        progression of the game's state, updates entities, and manages interactions such as movement,
        projectiles, and enemies.

        :param dt: The delta time since the last frame update
        :type dt: Float
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
        Handles the rendering logic based on the current game state. This method updates
        the visual output appropriately depending on whether the game is in a playing
        state or displaying menus, such as the start menu or game over screen.

        :raises AttributeError: If required attributes are not available or improperly defined.
        :raises TypeError: If attributes have incompatible types with the rendering logic.
        :raises RuntimeError: If the rendering operation cannot proceed due to the current state.

        :return: None
        """
        if self.config.state == "PLAYING":
            self.view.draw_world(self.model, self.item_manager, self.enemy_manager)
        elif self.config.state in ["START", "GAME OVER"]:
            self.view.draw_menu(self.menu_buttons, self.highlithed_button)

    def main_loop(self):
        """
        Executes the main application loop. This method continues to run until
        the `running` attribute is set to False. During each iteration, it
        manages the application framerate, processes events, updates the
        application's logic, and renders the visuals. The window title is
        updated with the current frames per second (FPS), and resources are
        cleaned up upon exit.

        :raises SystemExit: Exits the application when the loop concludes by
            quitting pygame and calling sys.exit().
        """
        while self.running:
            dt = self.clock.tick(self.config.display["fps"]) / 1000.0

            self._handle_events()
            self._update_logic(dt)
            self._render()

            pygame.display.set_caption(f"Schmopp - FPS: {int(self.clock.get_fps())}")

        pygame.quit()
        sys.exit()
