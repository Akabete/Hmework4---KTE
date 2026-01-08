import pygame
import random

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

    def item_picker(self, item_manager):
        for item in item_manager.items_spawned[:]:
            item_hitbox = pygame.Rect(item.coordinate_x, item.coordinate_y, self.config.item_size, self.config.item_size)

            if self.rect.colliderect(item_hitbox) and self.inventory.add_items(item):
                item_manager.items_spawned.remove(item)
                return


class Item:
    def __init__(self, config, coordinate_x, coordinate_y, name, texture, spawn_frequency):
        self.config = config
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y
        self.name = name
        self.texture = texture
        self.spawn_frequency = spawn_frequency

        self.hitbox = (self.coordinate_x, self.coordinate_y, self.config.item_size, self.config.item_size)

    def use(self, player):
        #default behaviour, simply for inheritances
        print(f"{self.name} cannot be used")


class Weapon(Item):
    def __init__(self, config, coordinate_x, coordinate_y, name, texture, spawn_frequency, damage, distance, explosion_radius):
        super().__init__(config, coordinate_x, coordinate_y, name, texture, spawn_frequency)
        self.damage = damage
        self.distance = distance
        self.explosion_radius = explosion_radius


class Food(Item):
    def __init__(self, config, coordinate_x, coordinate_y, name, texture, spawn_frequency, healage):
        super().__init__(config, coordinate_x, coordinate_y, name, texture, spawn_frequency)
        self.healage = healage

class Item_Manager:
    def __init__(self, config):
        self.config = config
        self.items_spawned = []

    def spawn_items(self):
        for i in range(50):
            rand_x = random.randint(0, self.config.map_size[0])
            rand_y = random.randint(0, self.config.map_size[1])

            roll = random.random()

            if self.config.frequency_melee[0] <= roll <= self.config.frequency_melee[1]:
                melee = Weapon(self.config, rand_x, rand_y, self.config.name_melee, self.config.melee_texture,
                             self.config.frequency_melee, self.config.damage_melee,
                             self.config.range_melee, self.config.explosion_radius_else)
                self.items_spawned.append(melee)

            elif self.config.frequency_pistol[0] <= roll <= self.config.frequency_pistol[1]:
                pistol = Weapon(self.config, rand_x, rand_y, self.config.name_pistol, self.config.pistol_texture,
                             self.config.frequency_pistol, self.config.damage_pistol,
                             self.config.range_pistol, self.config.explosion_radius_else)
                self.items_spawned.append(pistol)

            elif self.config.frequency_rifle[0] <= roll <= self.config.frequency_rifle[1]:
                rifle = Weapon(self.config, rand_x, rand_y, self.config.name_rifle, self.config.rifle_texture,
                            self.config.frequency_rifle, self.config.damage_rifle,
                            self.config.range_rifle, self.config.explosion_radius_else)
                self.items_spawned.append(rifle)

            elif roll == self.config.frequency_special:
                special = Weapon(self.config, rand_x, rand_y, self.config.name_special, self.config.special_texture,
                             self.config.frequency_special, self.config.damage_special,
                             self.config.range_special, self.config.explosion_radius_else)
                self.items_spawned.append(special)

            elif self.config.frequency_throwable[0] <= roll <= self.config.frequency_throwable[1]:
                throwable = Weapon(self.config, rand_x, rand_y, self.config.name_throwable, self.config.throwable_texture,
                             self.config.frequency_throwable, self.config.damage_throwable,
                             self.config.range_throwable, self.config.explosion_radius_throwable)
                self.items_spawned.append(throwable)


class Inventory:
    def __init__(self, capacity = 9):
        self.capacity = capacity
        self.slots = [None] * capacity
        self.selected_index = 0

    def add_items(self, item):
        if self.slots[self.selected_index] is None:
            self.slots[self.selected_index] = item
            return True

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