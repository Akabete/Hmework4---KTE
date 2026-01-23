import pygame
import random
import math

class Player:
    def __init__(self, config):
        self.config = config
        self.rect = pygame.Rect(
            300, 300,
            self.config.person_hitbox[0],
            self.config.person_hitbox[1]
        )

        self.position_x = float(self.rect.x)
        self.position_y = float(self.rect.y)
        self.speed = 300.0
        self.health = self.config.person_hp
        self.inventory = Inventory()
        self.current_vehicle = None

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
        self.speed = 150
        self.damage = self.config.enemy_damage
        self.last_attack_time = 0

        self.position_x = float(self.rect.x)
        self.position_y = float(self.rect.y)

        self.last_decision_time = 0
        self.direction = [0, 0]
        self.decision_time = 1000
        self.does_sprint = 0

        self.is_dead = False
        self.death_time = 0

    def random_movement(self, dt, player):
        if self.is_dead:
            return

        current_time = pygame.time.get_ticks()

        distance_to_player = math.sqrt( pow(self.position_x - player.position_x, 2) + pow(self.position_y - player.position_y, 2) )
        if distance_to_player < self.config.distance_to_chase:
            if player.position_x > self.position_x:
                self.direction[0] = 1
            elif player.position_x < self.position_x:
                self.direction[0] = -1
            else:
                self.direction[0] = 0

            if player.position_y > self.position_y:
                self.direction[1] = 1
            elif player.position_y < self.position_y:
                self.direction[1] = -1
            else:
                self.direction[1] = 0

            self.does_sprint = 1


        else:
            if current_time - self.last_decision_time > self.decision_time:
                self.direction[0] = random.randint(-1, 1)
                self.direction[1] = random.randint(-1, 1)
                self.does_sprint = random.randint(0, 1)
                self.last_decision_time = current_time

        self.move(self.direction[0], self.direction[1], self.does_sprint, dt)

        if self.rect.colliderect(player.rect):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > 1000:
                player.health -= self.damage
                print(f"Health: {player.health}")
                self.last_attack_time = current_time


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
            print(len(self.enemies_spawned))


    def replace_dead_enemies(self):
        for enemy in self.enemies_spawned[:]:
            if enemy.is_dead and pygame.time.get_ticks() -  enemy.death_time >= 5000:
                self.enemies_spawned.remove(enemy)
                self.spawn_enemies()


class Cars(Player):
    def __init__(self, config, coordinate_x, coordinate_y, texture, max_speed, acceleration, rotation_speed, health, hitbox, angle = 0, current_speed = 0):
        super().__init__(config)
        self.config = config
        self.cars_on_map = []

        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y
        self.texture = texture
        self.current_speed = current_speed
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.health = health
        self.rotation_speed = rotation_speed
        self.angle = angle

        self.rect = pygame.Rect(self.coordinate_x, self.coordinate_y, hitbox[0], hitbox[1])



    def drive(self, direction_x, direction_y, dt):
        if abs(self.current_speed) < self.max_speed:
            self.current_speed += self.acceleration * -direction_y * dt

        if direction_y == 0:
            self.current_speed -= self.acceleration * dt
        elif self.current_speed < 0:
            self.current_speed += self.acceleration * dt


        if abs(self.current_speed) > 1:
            self.angle += direction_x * self.rotation_speed * dt

        radians = math.radians(self.angle)

        change_x = self.current_speed * math.cos(radians) * dt
        change_y = self.current_speed * math.sin(radians) * dt

        self.position_x += change_x
        self.position_y += change_y

        self.rect.x = int(self.position_x)
        self.rect.y = int(self.position_y)

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


class Cars_Manager:
    def __init__(self, config):
        self.config = config
        self.cars_on_map = []

    def spawn_cars(self):

        spawn_offset = 1
        while len(self.cars_on_map) < self.config.vehicle_amount:

            bike = Cars(self.config, (self.config.vehicle_first_x * spawn_offset), self.config.vehicle_first_y,
                        self.config.vehicle_color_small, self.config.vehicle_speed_small,
                        self.config.vehicle_acceleration_small, self.config.vehicle_health_small,
                        self.config.vehicle_rotation_small, self.config.vehicle_hitbox_small)
            self.cars_on_map.append(bike)
            spawn_offset += 1

            car = Cars(self.config, (self.config.vehicle_first_x * spawn_offset), self.config.vehicle_first_y,
                       self.config.vehicle_color_medium, self.config.vehicle_speed_medium,
                       self.config.vehicle_acceleration_medium, self.config.vehicle_health_medium,
                       self.config.vehicle_rotation_medium, self.config.vehicle_hitbox_medium)
            self.cars_on_map.append(car)
            spawn_offset += 1

            tank = Cars(self.config, (self.config.vehicle_first_x * spawn_offset), self.config.vehicle_first_y,
                        self.config.vehicle_color_large, self.config.vehicle_speed_large,
                        self.config.vehicle_acceleration_large, self.config.vehicle_health_large,
                        self.config.vehicle_rotation_large, self.config.vehicle_hitbox_large)
            self.cars_on_map.append(tank)



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
                             self.config.frequency_melee, self.config.use_speed_melee, self.config.damage_melee,
                               self.config.range_melee, self.config.explosion_radius_else)
                self.items_spawned.append(melee)

            elif self.config.frequency_pistol[0] <= roll <= self.config.frequency_pistol[1]:
                pistol = Weapon(self.config, rand_x, rand_y, self.config.name_pistol, self.config.pistol_texture,
                               self.config.frequency_pistol, self.config.use_speed_pistol, self.config.damage_pistol,
                               self.config.range_pistol, self.config.explosion_radius_else)
                self.items_spawned.append(pistol)

            elif self.config.frequency_rifle[0] <= roll <= self.config.frequency_rifle[1]:
                rifle = Weapon(self.config, rand_x, rand_y, self.config.name_rifle, self.config.rifle_texture,
                               self.config.frequency_rifle, self.config.use_speed_rifle, self.config.damage_rifle,
                               self.config.range_rifle, self.config.explosion_radius_else)
                self.items_spawned.append(rifle)

            elif roll == self.config.frequency_special:
                special = Weapon(self.config, rand_x, rand_y, self.config.name_special, self.config.special_texture,
                               self.config.frequency_special, self.config.use_speed_special, self.config.damage_special,
                               self.config.range_special, self.config.explosion_radius_else)
                self.items_spawned.append(special)

            elif self.config.frequency_throwable[0] <= roll <= self.config.frequency_throwable[1]:
                throwable = Weapon(self.config, rand_x, rand_y, self.config.name_throwable, self.config.throwable_texture,
                               self.config.frequency_throwable, self.config.use_speed_throwable, self.config.damage_throwable,
                               self.config.range_throwable, self.config.explosion_radius_throwable)
                self.items_spawned.append(throwable)


class Projectile:
    def __init__(self, config, position_x, position_y, direction_x, direction_y, damage, speed, range, texture):
        self.config = config
        self.position_x = position_x
        self.position_y = position_y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.damage = damage
        self.speed = speed
        self.range = range
        self.distance_travelled = 0

        self.rect = pygame.Rect(position_x, position_y, 10, 10)

        self.texture = pygame.image.load(texture).convert_alpha()

    def move(self, dt):
        step_distance = self.speed * dt

        self.position_x += step_distance * self.direction_x
        self.position_y += step_distance * self.direction_y

        self.rect.x = int(self.position_x)
        self.rect.y = int(self.position_y)

        self.distance_travelled += step_distance

        if self.distance_travelled > self.range:
            return False

        return True


class Projectile_Manager:
    def __init__(self):
        self.bullets_on_map = []

    def add_projectile(self, projectile):
        self.bullets_on_map.append(projectile)

    def remove_projectile(self, projectile):
        self.bullets_on_map.remove(projectile)

    def move_projectiles(self, dt, enemy_manager, item_manager):
        for projectile in self.bullets_on_map[:]:
            if projectile.move(dt) is False:
                self.bullets_on_map.remove(projectile)
                continue

            for enemy in enemy_manager.enemies_spawned:
                if projectile.rect.colliderect(enemy.rect) and not enemy.is_dead:
                    enemy.health -= projectile.damage

                    if enemy.health <= 0:
                        enemy.is_dead = True
                        enemy.death_time = pygame.time.get_ticks()
                        enemy.item_dropper(item_manager)

                    self.remove_projectile(projectile)
                    break




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