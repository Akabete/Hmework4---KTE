import pygame


class Config:
    """
    Class representing the game configuration.
    """

    def __init__(self):
        """
        Initializes the Config class.
        :return: None
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
            "spawn_frequency": (0, 20),
            "damage": 100,
            "projectile_range": 50,
            "use_speed": 500,
            "explosion_radius": 0,
        }

        self.pistol = {
            "category": "pistol",
            "name": "Pistol",
            "texture": "assets/weapons/pistol.png",
            "spawn_frequency": (30, 40),
            "damage": 25,
            "projectile_range": 600,
            "use_speed": 300,
            "explosion_radius": 0,
        }

        self.rifle = {
            "category": "rifle",
            "name": "Rifle",
            "texture": "assets/weapons/rifle.png",
            "spawn_frequency": (50, 60),
            "damage": 15,
            "projectile_range": 800,
            "use_speed": 100,
            "explosion_radius": 0,
        }

        self.flamethrower = {
            "category": "special",
            "name": "Flamethrower",
            "texture": "assets/weapons/flamethrower.png",
            "spawn_frequency": (70, 80),
            "damage": 5,
            "projectile_range": 500,
            "use_speed": 50,
            "explosion_radius": 0,
        }

        self.grenade = {
            "category": "throwable",
            "name": "Grenade",
            "texture": "assets/weapons/grenade.png",
            "spawn_frequency": (90, 100),
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
        Loads the high score from a file.
        :return: Int
        """
        try:
            with open("highscore.txt", "r") as file:
                return int(file.read())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        """
        Saves the current high score to a file.
        :return: None
        """
        with open("highscore.txt", "w") as file:
            file.write(str(self.highscore))
