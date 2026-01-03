import pygame

class Player:
    def __init__(self, config):
        self.config = config
        self.rect = pygame.Rect(
            100, 100,
            self.config.person_hitbox[0],
            self.config.person_hitbox[1]
        )

        self.position_x = float(self.rect.x)
        self.position_y = float(self.rect.y)
        self.speed = 6.0

    def move(self, direction_x, direction_y, sprint):

        current_speed = self.speed
        if sprint:
            current_speed += 1.5

        if direction_x and direction_y:
            current_speed *= 0.7071

        change_x = direction_x * current_speed
        change_y = direction_y * current_speed

        self.position_x += change_x
        self.position_y += change_y

        self.rect.x += int(change_x)
        self.rect.y += int(change_y)

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > self.config.map_size[0]:
            self.rect.right = self.config.map_size[0]

        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom > self.config.map_size[1]:
            self.rect.bottom = self.config.map_size[1]