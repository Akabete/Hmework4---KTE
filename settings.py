class Config:
    def __init__(self):
        self.screen_size = (1200, 800)
        self.fps = 60

        self.map_size = (6000, 4000)
        self.map_texture = "assets/map_placeholder.png"

        self.person_hitbox = (40, 60)
        self.player_color = "red"

        self.vehicle_hitbox_small = (40, 60)
        self.vehicle_hitbox_small_color = "yellow"
        self.vehicle_hitbox_medium = (40, 60)
        self.vehicle_hitbox_medium_color = "green"
        self.vehicle_hitbox_large = (40, 60)
        self.vehicle_hitbox_large_color = "blue"


        self.inventory_slot = 64
        self.inventory_gap = 10

        self.item_size = 64
        self.item_in_hand_size = 32
        self.item_limit = 100


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

        self.damage_melee = 20
        self.damage_pistol = 15
        self.damage_rifle = 20
        self.damage_special = 5
        self.damage_throwable = 50

        self.range_melee = 5
        self.range_pistol = 20
        self.range_rifle = 50
        self.range_special = 10
        self.range_throwable = 100

        self.explosion_radius_throwable = 50
        self.explosion_radius_else = 0

