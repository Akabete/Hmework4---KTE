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
