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
        self.speed = 300.0
        self.inventory = Inventory()

    def move(self, direction_x, direction_y, sprint, dt):
        current_speed = self.speed
        if sprint:
            current_speed += 100.0

        if direction_x and direction_y:
            current_speed *= 0.7071


        change_x = direction_x * current_speed * dt
        change_y = direction_y * current_speed * dt

        self.position_x += change_x
        self.position_y += change_y

        self.rect.x = int(self.position_x)
        self.rect.y = int(self.position_y)

        print(f"Current Speed: {current_speed}")

        if self.rect.left < 0:
            self.rect.left = 0
            self.position_x = float(self.rect.x)
        elif self.rect.right > self.config.map_size[0]:
            self.rect.right = self.config.map_size[0]
            self.position_x = float(self.rect.x)

        if self.rect.top < 0:
            self.rect.top = 0
            self.position_y = float(self.rect.y)
        elif self.rect.bottom > self.config.map_size[1]:
            self.rect.bottom = self.config.map_size[1]
            self.position_y = float(self.rect.y)


class Item:
    def __init__(self, name, texture):
        self.name = name
        self.texture = texture

    def use(self, player):
        #default behaviour, simply for inheritances
        print(f"{self.name} cannot be used")

class Inventory:
    def __init__(self, capacity = 9):
        self.capacity = capacity
        self.slots = [None] * capacity
        self.selected_index = 0

    def add_items(self, item):
        for i in range(len(self.slots)):
            if self.slots[i] is None:
                self.slots[i] = item
                return True
        return False

    def select_slot(self, index):
        if 0 <= index < self.capacity:
            self.selected_index = index

    def scroll(self, direction):
        self.selected_index += direction
        self.selected_index %= self.capacity