import pygame
class Config:
    def __init__(self):
        self.state = "START"

        self.display = {
            "screen_size": (1200, 800),
            "fps": 60,
            "map_size": (6000, 4000),
            "map_texture": "assets/map_placeholder.png",
            "font": "assets/Pricedown Bl.otf"
        }

        self.player = {
            "hitbox": (40, 60),
            "texture": "black",
            "hp": 100,
            "spawn_location": (500, 500),
            "speed": 300.0,
            "sprint_bonus": 100.0
        }

        self.enemy = {
            "hitbox": (40, 60),
            "texture": "blue",
            "hp": 100,
            "speed": 150.0,
            "sprint_bonus": 100.0,
            "limit": 25,
            "damage": 10,
            "decision_speed": 1000,
            "attack_speed": 1000,
            "distance_to_chase": 300,
            "fade_time": 2500

        }

        self.combat = {
            "projectile_texture": "assets/bullet.png",
            "bullet_speed": 500,
            "grenade_speed": 300,
            "special_speed": 50,
            "bullet_limit": 200,
            "hand_distance": 30,
            "swing_strength": 80,
            "recoil_strength": 15
        }

        self.inventory_key_map = {
            pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2,
            pygame.K_4: 3, pygame.K_5: 4, pygame.K_6: 5,
            pygame.K_7: 6, pygame.K_8: 7, pygame.K_9: 8
            }

        self.vehicles = {
            "friction": 900,
            "amount": 3,
            "first_spawn_x": 100,
            "first_spawn_y": 100
        }

        self.bike = {
            "hiding": False,
            "hitbox": (30, 70),
            "texture": "red",
            "acceleration": 900.0,
            "max_speed": 900,
            "health": 50,
            "rotation_speed": 60.0
        }

        self.car = {
            "hiding": True,
            "hitbox": (50, 70),
            "texture": "green",
            "acceleration": 450.0,
            "max_speed": 800,
            "health": 100,
            "rotation_speed": 60.0
        }

        self.tank = {
            "hiding": True,
            "hitbox": (60, 80),
            "texture": "dark green",
            "acceleration": 50.0,
            "max_speed": 200,
            "health": 1000,
            "rotation_speed": 1.0
        }

        self.spawnable_vehicles = [
            self.bike,
            self.car,
            self.tank
        ]

        self.items = {
            "slot_size": 64,
            "inventory_gap": 10,
            "item_size": 64,
            "item_size_in_hand": 32,
            "item_limit": 50
        }

        self.crowbar = {
            "category": "melee",
            "name": "Crowbar",
            "texture": "assets/crowbar.png",
            "spawn_frequency": (0.0, 0.2),
            "damage": 100,
            "projectile_range": 50,
            "use_speed": 500,
            "explosion_radius": 0
        }

        self.pistol = {
            "category": "pistol",
            "name": "Pistol",
            "texture": "assets/pistol.png",
            "spawn_frequency": (0.3, 0.4),
            "damage": 25,
            "projectile_range": 600,
            "use_speed": 300,
            "explosion_radius": 0
        }

        self.rifle = {
            "category": "rifle",
            "name": "Rifle",
            "texture": "assets/rifle.png",
            "spawn_frequency": (0.5, 0.6),
            "damage": 15,
            "projectile_range": 800,
            "use_speed": 100,
            "explosion_radius": 0
        }

        self.flamethrower = {
            "category": "special",
            "name": "Flamethrower",
            "texture": "assets/flamethrower.png",
            "spawn_frequency": (0.7, 0.8),
            "damage": 5,
            "projectile_range": 500,
            "use_speed": 50,
            "explosion_radius": 0
        }

        self.grenade = {
            "category": "throwable",
            "name": "Grenade",
            "texture": "assets/grenade.png",
            "spawn_frequency": (0.9, 1.0),
            "damage": 50,
            "projectile_range": 1000,
            "use_speed": 500,
            "explosion_radius": 100
        }

        self.spawnable_weapons = [
            self.crowbar,
            self.pistol,
            self.rifle,
            self.flamethrower,
            self.grenade
        ]
