import pygame
from pygame import Color
import math
import random


class View:
    """
    Handles rendering of the main game components and manages textures for all in-game
    assets such as characters, vehicles, weapons, and maps. Provides functionality
    to update the screen according to the player's perspective, convert coordinates
    between world and screen systems, and manage dynamic and static visual elements
    within the game environment.

    This class is responsible for preloading textures for efficient runtime performance,
    calculating camera positions, and rendering visual elements including the player,
    enemies, vehicles, projectiles, ground items, and map layouts.

    :ivar screen: The screen surface used for rendering all game elements.
    :type screen: Pygame.Surface
    :ivar config: The configuration object containing game settings, texture paths,
        and other gameplay-related parameters.
    :type config: Object
    :ivar projectile_manager: An object that handles operations involving projectiles,
        such as their spawning, movement, and removal.
    :type projectile_manager: Object
    :ivar cars_manager: An object responsible for managing car-related gameplay elements,
        including their behavior and rendering.
    :type cars_manager: Object
    :ivar textures: A dictionary storing preloaded textures for various in-game assets,
        including players, enemies, vehicles, and weapons.
    :type textures: Dict
    :ivar hand_textures: A dictionary storing scaled textures for in-hand weapons and tools.
    :type hand_textures: Dict
    :ivar map_surface: A pre-rendered surface for the game map, created from the map
        texture and scaled to the appropriate size.
    :type map_surface: Pygame.Surface
    """
    def __init__(self, screen, config, projectile_manager, cars_manager):
        """
        Initializes the game’s main graphical and resource handling components, which include
        screen setup, configuration parsing, loading textures for various assets, and generating
        maps. The constructor preloads all required textures for players, enemies, vehicles, and
        weapons, ensuring optimized handling of assets during the game's runtime.

        :param screen: Screen surface used for rendering game elements.
        :type screen: Pygame.Surface
        :param config: Configuration object that contains game settings, texture paths, and
            other gameplay-related parameters.
        :type config: Object
        :param projectile_manager: Handles operations involving projectiles, including their
            spawning, movement, and removal.
        :type projectile_manager: Object
        :param cars_manager: Manages car-related aspects in the game such as behavior and rendering.
        :type cars_manager: Object
        """
        self.screen = screen
        self.config = config
        self.projectile_manager = projectile_manager
        self.cars_manager = cars_manager
        self.textures = {}
        self.hand_textures = {}
        self.textures[self.config.player["texture"]] = pygame.image.load(
            self.config.player["texture"]
        ).convert_alpha()
        self.textures[self.config.enemy["texture"]] = pygame.image.load(
            self.config.enemy["texture"]
        ).convert_alpha()
        for vehicle in self.config.spawnable_vehicles:
            path = vehicle["texture"]
            self.textures[path] = pygame.image.load(vehicle["texture"]).convert_alpha()

        for weapon_data in self.config.spawnable_weapons:
            path = weapon_data["texture"]
            full_sprite = pygame.image.load(path).convert_alpha()
            self.textures[path] = full_sprite

            size = self.config.items["item_size_in_hand"]
            self.hand_textures[path] = pygame.transform.scale(full_sprite, (size, size))

        self.map_surface = pygame.Surface(self.config.display["map_size"]).convert()
        map_texture = pygame.image.load(self.config.display["map_texture"]).convert()

        map_texture_image = pygame.transform.scale(
            map_texture, self.config.display["map_size"]
        )
        self.map_surface.blit(map_texture_image, (0, 0))

    def get_camera_rect(self, player):
        """
        Calculate the camera rectangle based on the position of the player and the
        configuration settings. This function ensures that the camera rectangle stays
        within the allowable limits of the map size, ensuring that the camera does not
        move outside the visible bounds of the map.

        :param player: The player object whose position is used to center the camera.
            It should have `centerx` and `centery` attributes to determine the
            target camera position.
        :return: A `pygame.Rect` object representing the calculated camera rectangle
            within the allowable limits based on map size and screen size.
        """
        target_x = player.centerx - (self.config.display["screen_size"][0] / 2)
        target_y = player.centery - (self.config.display["screen_size"][1] / 2)

        limit_x = (
            self.config.display["map_size"][0] - self.config.display["screen_size"][0]
        )
        limit_y = (
            self.config.display["map_size"][1] - self.config.display["screen_size"][1]
        )

        final_x = max(0, min(target_x, limit_x))
        final_y = max(0, min(target_y, limit_y))

        return pygame.Rect(
            final_x,
            final_y,
            self.config.display["map_size"][0],
            self.config.display["map_size"][1],
        )

    @staticmethod
    def world_to_screen(world_position, camera_rect):
        """
        Converts a position in the world coordinate system to a position in the screen coordinate system,
        based on the current camera rectangle's position.

        :param world_position: Tuple containing the x and y coordinates of a point in the world coordinate system.
        :param camera_rect: Rectangle object representing the current camera's position and dimensions in
            the world coordinate system.
        :return: A tuple containing the x and y coordinates of the position in the screen coordinate system.
        """
        screen_x = world_position[0] - camera_rect.x
        screen_y = world_position[1] - camera_rect.y
        return screen_x, screen_y

    def _draw_player(self, player_model, camera_rect):
        """
        Draws the player character on the screen if it is visible, transforms the world
        coordinates to screen coordinates, and optionally returns the player's screen
        rectangle if drawn.

        :param player_model: The model representing the player should have
            'visible' and 'rect' attributes.
        :type player_model: PlayerModel
        :param camera_rect: A rectangle representing the visible portion of the
            game world.
        :type camera_rect: Pygame.Rect
        :return: A Rect object representing the player's position on the screen
            or None if the player is not visible.
        :rtype: Optional[pygame.Rect]
        """
        if player_model.visible:
            screen_position = self.world_to_screen(
                player_model.rect.topleft, camera_rect
            )
            player_screen_rect = pygame.Rect(screen_position, player_model.rect.size)

            pygame.draw.rect(
                self.screen, self.config.player["hitbox_color"], player_screen_rect
            )
            sprite = self.textures[self.config.player["texture"]]
            self.screen.blit(sprite, screen_position)
            return player_screen_rect
        return None

    def _draw_enemies(self, enemy_manager, camera_rect):
        """
        Draws enemies on the screen, including their health bars and differentiates
        between live and dead enemies. Dead enemies are displayed in a specific manner,
        while live enemies are displayed with their health bar above them.

        :param enemy_manager: Manages the current state and list of all enemies.
        :type enemy_manager: EnemyManager
        :param camera_rect: The area in the game world currently visible on the screen.
        :type camera_rect: Pygame.Rect
        :return: None
        """
        current_time = pygame.time.get_ticks()

        for enemy in enemy_manager.enemies_spawned:
            screen_position = self.world_to_screen(enemy.rect.topleft, camera_rect)
            enemy_screen_rect = pygame.Rect(screen_position, enemy.rect.size)

            if enemy.hp <= 0:
                self._draw_dead_enemy(enemy, enemy_screen_rect, current_time)
            else:
                pygame.draw.rect(
                    self.screen, self.config.enemy["hitbox_color"], enemy_screen_rect
                )
                sprite = self.textures[self.config.enemy["texture"]]
                self.screen.blit(sprite, screen_position)

                bar_width = enemy.rect.width
                bar_height = self.config.enemy["healthbar_height"]
                bar_x = enemy_screen_rect.x
                bar_y = enemy_screen_rect.y - 10

                pygame.draw.rect(
                    self.screen, "red", (bar_x, bar_y, bar_width, bar_height)
                )
                health_ratio = max(0, enemy.hp / self.config.enemy["hp"])
                pygame.draw.rect(
                    self.screen,
                    "green",
                    (bar_x, bar_y, bar_width * health_ratio, bar_height),
                )

    def _draw_dead_enemy(self, enemy, screen_rect, current_time):
        """
        Draws a fading effect for a defeated enemy by creating a semi-transparent
        surface and gradually reducing its opacity over time.

        :param enemy: The enemy object with attributes such as death_time and rect.
        :type enemy: Object
        :param screen_rect: The rectangular area on the screen where the enemy's
            fading effect should be displayed.
        :type screen_rect: Pygame.Rect
        :param current_time: The current time in milliseconds, used to calculate
            the fade effect based on when the enemy was defeated.
        :type current_time: Int
        :return: None
        """
        time_passed = current_time - enemy.death_time

        fade_ratio = time_passed / self.config.enemy["fade_time"]
        alpha = max(0, 255 - int(fade_ratio * 255))

        # 3. Create the surface and apply transparency
        enemy_surface = pygame.Surface(enemy.rect.size).convert_alpha()
        enemy_surface.fill("red")
        enemy_surface.set_alpha(alpha)

        self.screen.blit(enemy_surface, screen_rect)

    def _draw_ground_items(self, item_manager, camera_rect):
        """
        Renders ground items that are currently within the game world.

        This method iterates over all items spawned in the game world and determines
        their screen position relative to the camera rectangle. It then draws the
        items on the game screen using their associated textures.

        :param item_manager: Manages all items within the game, providing access
            to the spawned items and their data.
        :param camera_rect: Defines the visible portion of the game world that
            the player can currently see, allowing for position calculations.
        :return: None
        """
        for item in item_manager.items_spawned:
            item_position = item.coordinate_x, item.coordinate_y
            screen_position = self.world_to_screen(item_position, camera_rect)

            self.screen.blit(self.textures[item.texture], screen_position)

    def _draw_vehicles(self, camera_rect):
        """
        Draws the vehicles on the screen within the given camera rectangle. This method
        translates the world position of vehicles to their corresponding screen position
        and renders their hitbox as a rectangle. It then blits the respective texture
        for each vehicle on the screen at the computed screen position.

        :param camera_rect: The rectangle representing the current view area of
            the camera in the world space.
        :type camera_rect: Pygame.Rect
        """
        for vehicle in self.cars_manager.cars_on_map:
            screen_position = self.world_to_screen(vehicle.rect.topleft, camera_rect)
            car_screen_rect = pygame.Rect(screen_position, vehicle.rect.size)

            pygame.draw.rect(self.screen, vehicle.hitbox_color, car_screen_rect)

            sprite = self.textures[vehicle.texture]
            self.screen.blit(sprite, screen_position)

    def _draw_projectiles(self, camera_rect):
        """
        Draws all projectiles currently active on the map by converting their world positions
        to screen positions within the provided camera rectangle and rendering them onto the
        screen. Each projectile is displayed using its texture at the appropriate location.

        :param camera_rect: The rectangle defining the current view of the camera in the world
            space.
        :type camera_rect: Rect
        """
        for projectile in self.projectile_manager.bullets_on_map:
            world_position = projectile.position_x, projectile.position_y
            screen_position = self.world_to_screen(world_position, camera_rect)

            self.screen.blit(projectile.texture, screen_position)

    def _get_item_offset(self, item, time_passed, dx):
        """
        Calculates the offset for the given item based on the time passed, direction, and item category.
        This function determines the offset by considering the item's swing or recoil strength,
        categories such as melee, throwable, or special and ensures specific offsets
        based on conditions like time or progress.

        :param item: The item for which the offset is being calculated.
        :type item: Object
        :param time_passed: The time elapsed since the item started being used.
        :type time_passed: Float
        :param dx: The direction in which the offset is applied (1 or -1).
        :type dx: Int
        :return: The calculated offset for the item based on the specific parameters.
        :rtype: Float
        """
        if time_passed > item.use_speed:
            return 0

        progress = time_passed / item.use_speed
        sin_value = math.sin(progress * math.pi)
        strength = self.config.combat["swing_strength"]
        recoil = self.config.combat["recoil_strength"]

        if "melee" in item.category or "throwable" in item.category:
            return -sin_value * strength if dx > 0 else sin_value * strength
        elif "special" in item.category:
            return random.randint(-3, 3) if time_passed < 100 else 0
        else:
            return sin_value * recoil if dx > 0 else -sin_value * recoil

    def _draw_rotated_item(self, item, angle, angle_deg, dx, player_rect):
        """
        Draws the rotated item on the screen.

        This method renders a rotated version of the specified item based on the provided
        angle and player position. It ensures proper flipping and alignment based on the
        direction indicated by `dx`. The method calculates the rotated sprite's position
        relative to the player's rectangle and renders it onto the screen.

        :param item: The item to be drawn, which includes a texture property.
        :param angle: The rotation angle in radians.
        :param angle_deg: The rotation angle in degrees for graphical transformations.
        :param dx: The horizontal direction of the item, used for flipping. A positive
            value indicates right, and a negative value indicates left.
        :param player_rect: The player's rectangle, used as a reference point for
            positioning the item.
        :return: None
        """
        sprite = self.hand_textures[item.texture]
        if dx < 0:
            sprite = pygame.transform.flip(sprite, False, True)

        rotated_sprite = pygame.transform.rotate(sprite, angle_deg)

        distance = self.config.combat["hand_distance"]
        offset_x = math.cos(angle) * distance
        offset_y = math.sin(angle) * distance

        target_position = player_rect.centerx + offset_x, player_rect.centery + offset_y

        rect = rotated_sprite.get_rect()
        if dx > 0:
            rect.midleft = target_position
        else:
            rect.midright = target_position

        self.screen.blit(rotated_sprite, rect)

    def _draw_held_item(self, player_model, player_screen_rect):
        """
        Draws the currently held item on the screen for the player.

        This method calculates the position and angle of the active item from the
        player's inventory and renders it on the screen at the appropriate rotation
        and position. The angle and offset of the item are dynamically calculated
        based on the player's screen location, mouse pointer position, and the time
        passed since the last item usage.

        :param player_model: The player model containing the inventory and selected
            item information.
        :type player_model: PlayerModel
        :param player_screen_rect: The rectangle surrounding the player's position on
            the screen.
        :type player_screen_rect: Pygame.Rect or None
        :return: None
        """
        if player_screen_rect is not None:
            active_item = player_model.inventory.slots[
                player_model.inventory.selected_index
            ]
            if active_item is not None:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                px, py = player_screen_rect.center
                dx, dy = mouse_x - px, mouse_y - py

                angle = math.atan2(dy, dx)
                angle_deg = -math.degrees(angle)

                time_passed = pygame.time.get_ticks() - active_item.last_use_time
                angle_deg += self._get_item_offset(active_item, time_passed, dx)

                self._draw_rotated_item(
                    active_item, angle, angle_deg, dx, player_screen_rect
                )

    def draw_inventory(self, player_model):
        """
        Draws the player's inventory on the screen by rendering item slots and contained
        items in a grid layout. Highlights the currently selected inventory slot and displays
        textures for items if present.

        :param player_model: The player object containing the inventory to be rendered.
        :type player_model: PlayerModel
        :return: None
        """
        inventory = player_model.inventory
        start_x = 5
        start_y = 5
        columns = 3

        for i in range(inventory.capacity):
            row = i // columns
            column = i % columns
            slot_x = start_x + (
                column * self.config.items["slot_size"]
                + (column * self.config.items["inventory_gap"])
                - 1
            )
            slot_y = start_y + (
                row * self.config.items["slot_size"]
                + (row * self.config.items["inventory_gap"])
                - 1
            )
            slot_rect = pygame.Rect(
                slot_x,
                slot_y,
                self.config.items["slot_size"],
                self.config.items["slot_size"],
            )

            if i == inventory.selected_index:
                color = Color(0, 0, 255, 128)
                width = 10
            else:
                color = "dark gray"
                width = 5

            pygame.draw.rect(self.screen, color, slot_rect, width)

            if inventory.slots[i] is not None:
                inventory_item = inventory.slots[i].texture
                item_texture = self.textures[inventory_item]

                self.screen.blit(item_texture, (slot_rect.x, slot_rect.y))

    def draw_world(self, player_model, item_manager, enemy_manager):
        """
        Draws the game world, including the map, player, items, enemies, and the UI, onto the
        screen surface. This function performs rendering updates for all visible components on the
        game world, ensuring the player perspective is centered based on the camera view.

        :param player_model: The player object containing the player's current status and attributes.
        :type player_model: PlayerModel
        :param item_manager: Manager responsible for handling interactable items on the ground or inventory.
        :type item_manager: ItemManager
        :param enemy_manager: Manager responsible for controlling and rendering enemy entities.
        :type enemy_manager: EnemyManager
        :return: None
        """
        camera_rect = self.get_camera_rect(player_model.rect)

        self.screen.fill("black")
        self.screen.blit(self.map_surface, (0, 0), camera_rect)

        self._draw_ground_items(item_manager, camera_rect)
        self._draw_vehicles(camera_rect)
        player_screen_rect = self._draw_player(player_model, camera_rect)
        self._draw_enemies(enemy_manager, camera_rect)
        self._draw_projectiles(camera_rect)

        self._draw_held_item(player_model, player_screen_rect)
        self.draw_inventory(player_model)
        self.draw_ui(player_model)

        pygame.display.flip()

    def draw_text(self, text, size, position_x, position_y, color):
        """
        Renders a text string onto the screen surface at a specified position.

        This function uses the Pygame library to render text with a specified
        font, size, color, and position. The text is horizontally centered
        relative to the provided x-coordinate.

        :param text: The string to be rendered on the screen.
        :type text: Str
        :param size: The size of the font to use for rendering the text.
        :type size: Int
        :param position_x: The x-coordinate of the horizontal center of the text.
        :type position_x: Int
        :param position_y: The y-coordinate where the text will be drawn.
        :type position_y: Int
        :param color: The color of the text to be rendered. Colors should be
            defined as RGB tuples (e.g., (255, 255, 255) for white).
        :type color: Tuple[int, int, int]
        :return: None. The function directly renders the text onto the screen
            surface.
        """
        font = pygame.font.Font(self.config.display["font"], size)
        text = font.render(text, True, color)
        self.screen.blit(text, (position_x - text.get_width() // 2, position_y))

    def draw_menu(self, buttons, highlited_index):
        """
        Draws the menu screen with buttons and highlighted selection.

        This method handles rendering of a menu with a title, optional game over
        information, and a selectable list of buttons. Title and other texts are
        displayed at specific positions based on the game state provided within the
        configuration and the highlighted button index.

        :param buttons: List of dictionaries where each dictionary describes a button.
            Each dictionary is expected to have a "text" key for the button text and
            a "rect" key for the button's pygame.Rect object.
        :param highlited_index: Integer index indicating which button is highlighted.
        :return: None
        """
        self.screen.fill("black")

        center_x = self.config.display["screen_size"][0] // 2
        title = "SCHMOPP" if self.config.state == "START" else "WASTED"
        color = "white" if title == "SCHMOPP" else "red"
        self.draw_text(title, 72, center_x, 100, color)
        if self.config.state == "GAME OVER":
            score_text = f"Final Score: {self.config.current_score}"
            best_score_text = f"Best Score: {self.config.highscore}"
            self.draw_text(score_text, 32, center_x, 180, "white")
            self.draw_text(best_score_text, 24, center_x, 220, "yellow")

        for i, button in enumerate(buttons):
            color = "white" if i == highlited_index else "gray25"
            pygame.draw.rect(self.screen, color, button["rect"], 3)
            self.draw_text(
                button["text"], 36, button["rect"].centerx, button["rect"].y + 50, color
            )

        pygame.display.flip()

    def draw_ui(self, player):
        """
        Generates and displays UI elements such as health and score for the player.

        This method is responsible for rendering textual representations
        of key gameplay metrics, such as the player's current health and
        score, on the screen.

        :param player: The player object containing the `hp` attribute for
            health display.
        :return: None
        """
        health_text = f"Health: {player.hp}"
        self.draw_text(health_text, 36, 1050, 30, "blue")

        score_text = f"Score: {self.config.current_score}"
        self.draw_text(score_text, 36, 1050, 80, "blue")
