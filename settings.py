class Config:
    def __init__(self):
        self.screen_size = (1200, 800)
        self.fps = 60

        self.map_size = (6000, 4000)
        self.map_texture = "assets/map_placeholder.png"

        self.person_hitbox = (40, 60)
        self.player_color = "black"
        self.enemy_color = "blue"
        self.person_hp = 100

        self.vehicle_amount = 3
        self.vehicle_first_x = 100
        self.vehicle_first_y = 100

        self.vehicle_hitbox_small = (30, 70)
        self.vehicle_color_small = "red"
        self.vehicle_acceleration_small = 900.0
        self.vehicle_speed_small = 900
        self.vehicle_health_small = 70
        self.vehicle_rotation_small = 90.0

        self.vehicle_hitbox_medium = (50, 70)
        self.vehicle_color_medium = "green"
        self.vehicle_acceleration_medium = 450.0
        self.vehicle_speed_medium = 800
        self.vehicle_health_medium = 20
        self.vehicle_rotation_medium = 60.0

        self.vehicle_hitbox_large = (60, 80)
        self.vehicle_color_large = "dark green"
        self.vehicle_acceleration_large = 150.0
        self.vehicle_speed_large = 500
        self.vehicle_health_large = 500
        self.vehicle_rotation_large = 30.0

        self.weapon_bullet_speed = 500
        self.weapon_grenade_speed = 300
        self.weapon_special_speed = 50


        self.inventory_slot = 64
        self.inventory_gap = 10

        self.item_size = 64
        self.item_in_hand_size = 32
        self.item_limit = 100

        self.enemy_limit = 25
        self.enemy_damage = 10
        self.distance_to_chase = 300


        self.name_melee = "Crowbar"
        self.name_pistol = "Pistol"
        self.name_rifle = "Rifle"
        self.name_special = "Flamethrower"
        self.name_throwable = "Grenade"

        self.melee_texture = "assets/crowbar.png"
        self.pistol_texture = "assets/pistol.png"
        self.rifle_texture = "assets/rifle.png"
        self.special_texture = "assets/flamethrower.png"
        self.throwable_texture = "assets/grenade.png"

        self.frequency_melee = (0.0, 0.2)
        self.frequency_pistol = (0.3, 0.4)
        self.frequency_rifle = (0.5, 0.6)
        self.frequency_special = 0.7
        self.frequency_throwable = (0.8, 0.9)

        self.weapon_bullet_limit = 200
        self.projectile_texture = "assets/bullet.png"

        self.damage_melee = 20
        self.damage_pistol = 15
        self.damage_rifle = 20
        self.damage_special = 5
        self.damage_throwable = 50

        self.range_melee = 50
        self.range_pistol = 600
        self.range_rifle = 800
        self.range_special = 500
        self.range_throwable = 1000

        self.use_speed_melee = 500
        self.use_speed_pistol = 300
        self.use_speed_rifle = 100
        self.use_speed_special = 50
        self.use_speed_throwable = 1500

        self.explosion_radius_throwable = 50
        self.explosion_radius_else = 0

