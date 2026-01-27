import pygame


class Config:
    def __init__(self):
        """
        Represents the configuration and state management for a game environment.

        This class provides a centralized location for managing various game properties,
        including game state, menu options, player attributes, enemy characteristics,
        combat mechanics, inventory settings, vehicle details, item properties,
        and weapon configurations. The attributes are structured to ensure
        easy extensibility and readability for further development.

        Attributes
        ----------
        :ivar str state:
            The current state of the game, starting with "START".
        :ivar int current_score:
            The current score of the game.
        highscore: int
            The highest recorded score, loaded using the load_high_score method.
        menu_options: list of str
            A list of menu options available to the player.
        menu_buttons: dict
            Configuration for the properties of menu buttons, such as width and height.
        display: dict
            Configuration for display-related properties like screen size and FPS.
        player: dict
            Properties related to the player, such as hitbox and speed.
        enemy: dict
            Properties related to enemies, such as speed and decision-making.
        combat: dict
            Configuration for combat mechanics, like projectile speed and recoil.
        inventory_key_map: dict
            Mapping of inventory slots to keyboard keys for quick access.
        vehicles: dict
            General configuration for vehicles, like spawn position and friction.
        bike: dict
            Detailed properties for the bike vehicle, such as speed and health.
        car: dict
            Detailed properties for the car vehicle, including hiding capability.
        tank: dict
            Specifications for the tank vehicle, focusing on durability and power.
        spawnable_vehicles: list of dict
            A list of vehicles that can be spawned in the game environment.
        items: dict
            Configuration related to item properties, like size and inventory capacity.
        crowbar: dict
            Configuration for the crowbar weapon, including damage and usage speed.
        pistol: dict
            Configuration for the pistol weapon, specifying damage and range.
        rifle: dict
            Definitions for the rifle weapon, highlighting its long-range capabilities.
        flamethrower: dict
            Configuration for the flamethrower weapon, with a focus on special abilities.
        grenade: dict
            Definitions for the grenade weapon, detailing its explosion effects.
        spawnable_weapons: list of dict
            A list of weapons that can be spawned in the game world.
        """
        self.state = "START"
        self.current_score = 0
        self.highscore = self.load_high_score()
        self.menu_options = ["START GAME", "OPTIONS", "QUIT GAME"]

        self.menu_buttons = {
            "width": 300,
            "height": 150,
            "padding": 20,
            "menu_first_y": 250,
        }

        self.display = {
            "screen_size": (1200, 800),
            "fps": 60,
            "map_size": (6000, 4000),
            "map_texture": "assets/map_placeholder.png",
            "font": "assets/Pricedown Bl.otf",
        }

        self.player = {
            "hitbox": (40, 60),
            "hitbox_color": "black",
            "texture": "assets/people/player.png",
            "hp": 100,
            "spawn_location": (200, 200),
            "speed": 300.0,
            "sprint_bonus": 100.0,
        }

        self.enemy = {
            "hitbox": (40, 60),
            "hitbox_color": "blue",
            "texture": "assets/people/enemy.png",
            "hp": 100,
            "speed": 150.0,
            "sprint_bonus": 100.0,
            "limit": 25,
            "damage": 10,
            "decision_speed": 1000,
            "attack_speed": 1000,
            "distance_to_chase": 300,
            "fade_time": 2500,
            "points_given": 100,
            "healthbar_height": 5,
        }

        self.combat = {
            "projectile_texture": "assets/weapons/bullet.png",
            "bullet_speed": 500,
            "grenade_speed": 300,
            "special_speed": 50,
            "bullet_limit": 200,
            "hand_distance": 30,
            "swing_strength": 80,
            "recoil_strength": 15,
        }

        self.inventory_key_map = {
            pygame.K_1: 0,
            pygame.K_2: 1,
            pygame.K_3: 2,
            pygame.K_4: 3,
            pygame.K_5: 4,
            pygame.K_6: 5,
            pygame.K_7: 6,
            pygame.K_8: 7,
            pygame.K_9: 8,
        }

        self.vehicles = {
            "friction": 900,
            "amount": 3,
            "first_spawn_x": 100,
            "first_spawn_y": 100,
        }

        self.bike = {
            "hiding": False,
            "hitbox": (30, 70),
            "hitbox_color": "red",
            "texture": "assets/vehicles/bike.png",
            "acceleration": 900.0,
            "max_speed": 900,
            "health": 50,
            "rotation_speed": 90.0,
        }

        self.car = {
            "hiding": True,
            "hitbox": (50, 70),
            "hitbox_color": "green",
            "texture": "assets/vehicles/car.png",
            "acceleration": 450.0,
            "max_speed": 800,
            "health": 100,
            "rotation_speed": 60.0,
        }

        self.tank = {
            "hiding": True,
            "hitbox": (60, 80),
            "hitbox_color": "dark green",
            "texture": "assets/vehicles/tank.png",
            "acceleration": 50.0,
            "max_speed": 200,
            "health": 1000,
            "rotation_speed": 30.0,
        }

        self.spawnable_vehicles = [self.bike, self.car, self.tank]

        self.items = {
            "slot_size": 64,
            "inventory_gap": 10,
            "item_size": 64,
            "item_size_in_hand": 32,
            "item_limit": 50,
        }

        self.crowbar = {
            "category": "melee",
            "name": "Crowbar",
            "texture": "assets/weapons/crowbar.png",
            "spawn_frequency": (0.0, 0.2),
            "damage": 100,
            "projectile_range": 50,
            "use_speed": 500,
            "explosion_radius": 0,
        }

        self.pistol = {
            "category": "pistol",
            "name": "Pistol",
            "texture": "assets/weapons/pistol.png",
            "spawn_frequency": (0.3, 0.4),
            "damage": 25,
            "projectile_range": 600,
            "use_speed": 300,
            "explosion_radius": 0,
        }

        self.rifle = {
            "category": "rifle",
            "name": "Rifle",
            "texture": "assets/weapons/rifle.png",
            "spawn_frequency": (0.5, 0.6),
            "damage": 15,
            "projectile_range": 800,
            "use_speed": 100,
            "explosion_radius": 0,
        }

        self.flamethrower = {
            "category": "special",
            "name": "Flamethrower",
            "texture": "assets/weapons/flamethrower.png",
            "spawn_frequency": (0.7, 0.8),
            "damage": 5,
            "projectile_range": 500,
            "use_speed": 50,
            "explosion_radius": 0,
        }

        self.grenade = {
            "category": "throwable",
            "name": "Grenade",
            "texture": "assets/weapons/grenade.png",
            "spawn_frequency": (0.9, 1.0),
            "damage": 50,
            "projectile_range": 1000,
            "use_speed": 500,
            "explosion_radius": 100,
        }

        self.spawnable_weapons = [
            self.crowbar,
            self.pistol,
            self.rifle,
            self.flamethrower,
            self.grenade,
        ]

    @staticmethod
    def load_high_score():
        """
        Loads the high score from a file named 'highscore.txt'.

        If the file does not exist or contains invalid data (e.g., not an integer),
        the method returns 0 as the default high score.

        :return: The loaded high score as an integer, or 0 if there are issues reading or
                 interpreting the file.
        :rtype: Int
        """
        try:
            with open("highscore.txt", "r") as file:
                return int(file.read())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        """
        Saves the current high score to a file.

        This method writes the value of the 'highscore'
        attribute to a file named 'highscore.txt'. The file
        is created if it does not exist and overwritten if it does.

        :return: None
        """
        with open("highscore.txt", "w") as file:
            file.write(str(self.highscore))
