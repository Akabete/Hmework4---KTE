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
        self.health = self.config.person_hp
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

    def item_dropper(self, item_manager):
        item_to_drop = self.inventory.slots[self.inventory.selected_index]
        if item_to_drop is not None:
            item_to_drop.coordinate_x = self.rect.x
            item_to_drop.coordinate_y = self.rect.y

            item_manager.items_spawned.append(item_to_drop)
            self.inventory.slots[self.inventory.selected_index] = None


class Enemy(Player):
    def __init__(self, config):
        super().__init__(config)
        spawn_position_x = random.randint(0, self.config.map_size[0])
        spawn_position_y = random.randint(0, self.config.map_size[1])
        self.rect = pygame.Rect(spawn_position_x, spawn_position_y, self.config.person_hitbox[0], self.config.person_hitbox[1])

        self.position_x = float(self.rect.x)
        self.position_y = float(self.rect.y)

        self.last_decision_time = 0
        self.direction = [0, 0]
        self.decision_time = 1000
        self.does_sprint = 0

    def random_movement(self, dt, player):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_decision_time > self.decision_time:
            self.direction[0] = random.randint(-1, 1)
            self.direction[1] = random.randint(-1, 1)
            self.does_sprint = random.randint(0, 1)
            self.last_decision_time = current_time

        self.move(self.direction[0], self.direction[1], self.does_sprint, dt)


class Enemy_Manager:
    def __init__(self, config):
        self.enemies_spawned = []
        self.config = config

    def spawn_enemies(self):
        while len(self.enemies_spawned) < self.config.enemy_limit:
            enemy = Enemy(self.config)

            roll = random.random()

            if self.config.frequency_melee[0] <= roll <= self.config.frequency_melee[1]:
                melee = Weapon(self.config, 0, 0, self.config.name_melee, self.config.melee_texture,
                               self.config.frequency_melee, self.config.damage_melee,
                               self.config.range_melee, self.config.explosion_radius_else, self.config.use_speed_melee)
                enemy.inventory.slots[0] =  melee

            elif self.config.frequency_pistol[0] <= roll <= self.config.frequency_pistol[1]:
                pistol = Weapon(self.config, 0, 0, self.config.name_pistol, self.config.pistol_texture,
                                self.config.frequency_pistol, self.config.damage_pistol,
                                self.config.range_pistol, self.config.explosion_radius_else,
                                self.config.use_speed_pistol)
                enemy.inventory.slots[0] =  pistol

            elif self.config.frequency_rifle[0] <= roll <= self.config.frequency_rifle[1]:
                rifle = Weapon(self.config, 0, 0, self.config.name_rifle, self.config.rifle_texture,
                               self.config.frequency_rifle, self.config.damage_rifle,
                               self.config.range_rifle, self.config.explosion_radius_else, self.config.use_speed_rifle)
                enemy.inventory.slots[0] = rifle

            elif roll == self.config.frequency_special:
                special = Weapon(self.config, 0, 0, self.config.name_special, self.config.special_texture,
                                 self.config.frequency_special, self.config.damage_special,
                                 self.config.range_special, self.config.explosion_radius_else,
                                 self.config.use_speed_special)
                enemy.inventory.slots[0] = special

            elif self.config.frequency_throwable[0] <= roll <= self.config.frequency_throwable[1]:
                throwable = Weapon(self.config, 0, 0, self.config.name_throwable,
                                   self.config.throwable_texture,
                                   self.config.frequency_throwable, self.config.damage_throwable,
                                   self.config.range_throwable, self.config.explosion_radius_throwable,
                                   self.config.use_speed_throwable)
                enemy.inventory.slots[0] =  throwable

            self.enemies_spawned.append(enemy)



class Item:
    def __init__(self, config, coordinate_x, coordinate_y, name, texture, spawn_frequency, use_speed):
        self.config = config
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y
        self.name = name
        self.texture = texture
        self.spawn_frequency = spawn_frequency
        self.use_speed = use_speed

        self.hitbox = (self.coordinate_x, self.coordinate_y, self.config.item_size, self.config.item_size)

        self.last_use_time = 0


    def use(self, player):
        #default behaviour, simply for inheritances
        print(f"{self.name} cannot be used")


class Weapon(Item):
    def __init__(self, config, coordinate_x, coordinate_y, name, texture, spawn_frequency, use_speed, damage, distance, explosion_radius):
        super().__init__(config, coordinate_x, coordinate_y, name, texture, spawn_frequency, use_speed)
        self.damage = damage
        self.distance = distance
        self.explosion_radius = explosion_radius


class Food(Item):
    def __init__(self, config, coordinate_x, coordinate_y, name, texture, spawn_frequency, use_speed, healage):
        super().__init__(config, coordinate_x, coordinate_y, name, texture, spawn_frequency, use_speed)
        self.healage = healage

class Item_Manager:
    def __init__(self, config):
        self.config = config
        self.items_spawned = []

    def spawn_items(self):
        for i in range(self.config.item_limit):
            rand_x = random.randint(0, self.config.map_size[0])
            rand_y = random.randint(0, self.config.map_size[1])

            roll = random.random()

            if self.config.frequency_melee[0] <= roll <= self.config.frequency_melee[1]:
                melee = Weapon(self.config, rand_x, rand_y, self.config.name_melee, self.config.melee_texture,
                             self.config.frequency_melee, self.config.damage_melee,
                             self.config.range_melee, self.config.explosion_radius_else, self.config.use_speed_melee)
                self.items_spawned.append(melee)

            elif self.config.frequency_pistol[0] <= roll <= self.config.frequency_pistol[1]:
                pistol = Weapon(self.config, rand_x, rand_y, self.config.name_pistol, self.config.pistol_texture,
                             self.config.frequency_pistol, self.config.damage_pistol,
                             self.config.range_pistol, self.config.explosion_radius_else, self.config.use_speed_pistol)
                self.items_spawned.append(pistol)

            elif self.config.frequency_rifle[0] <= roll <= self.config.frequency_rifle[1]:
                rifle = Weapon(self.config, rand_x, rand_y, self.config.name_rifle, self.config.rifle_texture,
                            self.config.frequency_rifle, self.config.damage_rifle,
                            self.config.range_rifle, self.config.explosion_radius_else, self.config.use_speed_rifle)
                self.items_spawned.append(rifle)

            elif roll == self.config.frequency_special:
                special = Weapon(self.config, rand_x, rand_y, self.config.name_special, self.config.special_texture,
                             self.config.frequency_special, self.config.damage_special,
                             self.config.range_special, self.config.explosion_radius_else, self.config.use_speed_special)
                self.items_spawned.append(special)

            elif self.config.frequency_throwable[0] <= roll <= self.config.frequency_throwable[1]:
                throwable = Weapon(self.config, rand_x, rand_y, self.config.name_throwable, self.config.throwable_texture,
                             self.config.frequency_throwable, self.config.damage_throwable,
                             self.config.range_throwable, self.config.explosion_radius_throwable, self.config.use_speed_throwable)
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