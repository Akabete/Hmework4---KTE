import pygame
import random
import math


class Player:
    """
    Class representing the player.
    :attrib config: The configuration of the game.
    """
    def __init__(self, config):
        """
        Initializes the Player class.
        :param config: The configuration of the game.
        :return: None
        """
        self.config = config
        player_settings = self.config.player
        start_x, start_y = player_settings["spawn_location"]

        self.rect = pygame.Rect(
            start_x, start_y, player_settings["hitbox"][0], player_settings["hitbox"][1]
        )
        self.position_x = float(start_x)
        self.position_y = float(start_y)
        self.hp = player_settings["hp"]
        self.speed = player_settings["speed"]
        self.sprint_bonus = player_settings["sprint_bonus"]

        self.inventory = Inventory()
        self.current_vehicle = None
        self.visible = True

    def move(self, direction_x, direction_y, sprint, dt):
        """
        Moves the player.
        :param direction_x: The movement in X direction.
        :param direction_y: The movement in Y direction.
        :param sprint: Whether the player is sprinting.
        :param dt: The time passed since the last frame.
        :return: None
        """
        current_speed = self.speed
        if sprint:
            current_speed += self.sprint_bonus

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
        elif self.rect.right > self.config.display["map_size"][0]:
            self.rect.right = self.config.display["map_size"][0]
            self.position_x = float(self.rect.x)

        if self.rect.top < 0:
            self.rect.top = 0
            self.position_y = float(self.rect.y)
        elif self.rect.bottom > self.config.display["map_size"][1]:
            self.rect.bottom = self.config.display["map_size"][1]
            self.position_y = float(self.rect.y)

    def sync_with_vehicle(self):
        """
        Synchronizes the player's position with the current vehicle.
        :return: None
        """
        if self.current_vehicle is not None:
            self.rect.center = self.current_vehicle.rect.center
            self.position_x = float(self.rect.centerx)
            self.position_y = float(self.rect.centery)

    def item_picker(self, item_manager):
        """
        Picks up an item from the ground.
        :param item_manager: The item manager.
        :return: None
        """
        for item in item_manager.items_spawned[:]:
            item_hitbox = pygame.Rect(
                item.coordinate_x,
                item.coordinate_y,
                self.config.items["item_size"],
                self.config.items["item_size"],
            )

            if self.rect.colliderect(item_hitbox) and self.inventory.add_items(item):
                item_manager.items_spawned.remove(item)
                return

    def item_dropper(self, item_manager):
        """
        Drops the currently selected item.
        :param item_manager: The item manager.
        :return: None
        """
        item_to_drop = self.inventory.slots[self.inventory.selected_index]
        if item_to_drop is not None:
            item_to_drop.coordinate_x = self.rect.x
            item_to_drop.coordinate_y = self.rect.y

            item_manager.items_spawned.append(item_to_drop)
            self.inventory.slots[self.inventory.selected_index] = None


class Enemy(Player):
    """
    Class representing an enemy.
    :attrib config: The configuration of the game.
    :attrib start_x: The starting X coordinate.
    :attrib start_y: The starting Y coordinate.
    """
    def __init__(self, config, start_x, start_y):
        """
        Initializes the Enemy class.
        :param config: The configuration of the game.
        :param start_x: The starting X coordinate.
        :param start_y: The starting Y coordinate.
        :return: None
        """
        super().__init__(config)
        self.hp = self.config.enemy["hp"]
        self.damage = self.config.enemy["damage"]
        self.death_time = 0
        self.last_decision_time = 0
        self.last_attack_time = 0
        self.direction: list = [0, 0]
        self.does_sprint = False
        self.sprint_bonus = self.config.enemy["sprint_bonus"]

        self.position_x = float(start_x)
        self.position_y = float(start_y)

        self.rect.x = int(self.position_x)
        self.rect.y = int(self.position_y)

    def think(self, player):
        """
        Handles the enemy AI logic.
        :param player: The player object.
        :return: None
        """
        if self.hp <= 0:
            return

        current_time = pygame.time.get_ticks()
        direction_x = self.position_x - player.position_x
        direction_y = self.position_y - player.position_y
        distance = math.sqrt((direction_x**2) + (direction_y**2))

        if distance <= self.config.enemy["distance_to_chase"]:
            distance_x = player.position_x - self.position_x
            distance_y = player.position_y - self.position_y

            if distance > 0:
                self.direction[0] = distance_x / distance
                self.direction[1] = distance_y / distance

            self.does_sprint = True
        else:
            self.does_sprint = False
            if (
                current_time - self.last_decision_time
                > self.config.enemy["decision_speed"]
            ):
                angle = random.uniform(0, 2 * math.pi)
                self.direction[0] = math.cos(angle)
                self.direction[1] = math.sin(angle)

                self.last_decision_time = current_time

    def update(self, dt, player):
        """
        Updates the enemy state.
        :param dt: The time passed since the last frame.
        :param player: The player object.
        :return: None
        """
        if self.hp <= 0:
            return

        self.move(self.direction[0], self.direction[1], self.does_sprint, dt)

        if self.rect.colliderect(player.rect):
            current_time = pygame.time.get_ticks()
            if current_time - self.last_attack_time > self.config.enemy["attack_speed"]:
                player.hp -= self.damage
                print(f"Health: {player.hp}")
                self.last_attack_time = current_time


class Enemy_Manager:
    """
    Class responsible for managing enemies.
    :attrib config: The configuration of the game.
    """
    def __init__(self, config):
        """
        Initializes the Enemy_Manager class.
        :param config: The configuration of the game.
        :return: None
        """
        self.enemies_spawned = []
        self.config = config

    def spawn_enemies(self):
        """
        Spawns enemies on the map.
        :return: None
        """
        while len(self.enemies_spawned) < self.config.enemy["limit"]:
            spawn_x = random.randint(0, self.config.display["map_size"][0])
            spawn_y = random.randint(0, self.config.display["map_size"][1])
            enemy = Enemy(self.config, spawn_x, spawn_y)

            roll = random.randint(1, 100)

            for weapon in self.config.spawnable_weapons:
                low, high = weapon["spawn_frequency"]

                if low <= roll <= high:
                    new_item = Weapon(self.config, 0, 0, **weapon)
                    enemy.inventory.slots[0] = new_item
                    break

            self.enemies_spawned.append(enemy)
            print(len(self.enemies_spawned))

    def replace_dead_enemies(self):
        """
        Replaces dead enemies.
        :return: None
        """
        for enemy in self.enemies_spawned[:]:
            if (
                enemy.hp <= 0
                and pygame.time.get_ticks() - enemy.death_time
                >= self.config.enemy["fade_time"]
            ):
                self.enemies_spawned.remove(enemy)
                self.spawn_enemies()

    def reset_manager(self):
        """
        Resets the enemy manager.
        :return: None
        """
        self.enemies_spawned.clear()
        self.spawn_enemies()


class Cars:
    """
    Class representing a vehicle.
    :attrib config: The configuration of the game.
    :attrib coordinate_x: The X coordinate.
    :attrib coordinate_y: The Y coordinate.
    :attrib texture: The texture of the vehicle.
    :attrib max_speed: The maximum speed of the vehicle.
    :attrib acceleration: The acceleration of the vehicle.
    :attrib rotation_speed: The rotation speed of the vehicle.
    :attrib health: The health of the vehicle.
    :attrib hitbox: The hitbox of the vehicle.
    :attrib hiding: Whether the vehicle hides the player.
    :attrib hitbox_color: The color of the hitbox.
    :attrib angle: The angle of the vehicle.
    :attrib current_speed: The current speed of the vehicle.
    """
    def __init__(
        self,
        config,
        coordinate_x,
        coordinate_y,
        texture,
        max_speed,
        acceleration,
        rotation_speed,
        health,
        hitbox,
        hiding,
        hitbox_color,
        angle=0,
        current_speed=0,
    ):
        """
        Initializes the Cars class.
        :param config: The configuration of the game.
        :param coordinate_x: The X coordinate.
        :param coordinate_y: The Y coordinate.
        :param texture: The texture of the vehicle.
        :param max_speed: The maximum speed of the vehicle.
        :param acceleration: The acceleration of the vehicle.
        :param rotation_speed: The rotation speed of the vehicle.
        :param health: The health of the vehicle.
        :param hitbox: The hitbox of the vehicle.
        :param hiding: Whether the vehicle hides the player.
        :param hitbox_color: The color of the hitbox.
        :param angle: The angle of the vehicle.
        :param current_speed: The current speed of the vehicle.
        :return: None
        """
        self.config = config

        self.rect = pygame.Rect(coordinate_x, coordinate_y, hitbox[0], hitbox[1])
        self.position_x = float(coordinate_x)
        self.position_y = float(coordinate_y)

        self.texture = texture
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.rotation_speed = rotation_speed
        self.health = health
        self.hiding = hiding
        self.hitbox_color = hitbox_color

        self.current_speed = current_speed
        self.angle = angle

    def _acceleration(self, direction_y, dt):
        """
        Handles the acceleration of the vehicle.
        :param direction_y: The movement in Y direction.
        :param dt: The time passed since the last frame.
        :return: None
        """
        if direction_y != 0:
            push_direction = -direction_y

            if push_direction > 0 and self.current_speed < self.max_speed:
                self.current_speed += self.acceleration * dt
            elif push_direction < 0 and self.current_speed > -self.max_speed:
                self.current_speed -= self.acceleration * dt

        else:
            if self.current_speed > 0:
                self.current_speed -= self.config.vehicles["friction"] * dt
                if self.current_speed < 0:
                    self.current_speed = 0

            elif self.current_speed < 0:
                self.current_speed += self.config.vehicles["friction"] * dt
                if self.current_speed > 0:
                    self.current_speed = 0

    def _physics(self, direction_x, dt):
        """
        Handles the physics of the vehicle.
        :param direction_x: The movement in X direction.
        :param dt: The time passed since the last frame.
        :return: None
        """
        radians = math.radians(self.angle)

        change_x = self.current_speed * math.cos(radians) * dt
        change_y = self.current_speed * math.sin(radians) * dt

        self.position_x += change_x
        self.position_y += change_y

        self.rect.x = int(self.position_x)
        self.rect.y = int(self.position_y)

        if abs(self.current_speed) > 1:
            self.angle += direction_x * self.rotation_speed * dt

    def _boundaries(self):
        """
        Handles the boundaries for the vehicle.
        :return: None
        """
        if self.rect.left < 0:
            self.rect.left = 0
            self.position_x = float(self.rect.x)
            self.current_speed = 0
        elif self.rect.right > self.config.display["map_size"][0]:
            self.rect.right = self.config.display["map_size"][0]
            self.position_x = float(self.rect.x)
            self.current_speed = 0

        if self.rect.top < 0:
            self.rect.top = 0
            self.position_y = float(self.rect.y)
            self.current_speed = 0
        elif self.rect.bottom > self.config.display["map_size"][1]:
            self.rect.bottom = self.config.display["map_size"][1]
            self.position_y = float(self.rect.y)
            self.current_speed = 0

    def drive(self, direction_x, direction_y, dt):
        """
        Handles driving the vehicle.
        :param direction_x: The movement in X direction.
        :param direction_y: The movement in Y direction.
        :param dt: The time passed since the last frame.
        :return: None
        """
        self._physics(direction_x, dt)
        self._acceleration(direction_y, dt)
        self._boundaries()


class Cars_Manager:
    """
    Class responsible for managing vehicles.
    :attrib config: The configuration of the game.
    """
    def __init__(self, config):
        """
        Initializes the Cars_Manager class.
        :param config: The configuration of the game.
        :return: None
        """
        self.config = config
        self.cars_on_map = []

    def spawn_cars(self):
        """
        Spawns cars on the map.
        :return: None
        """
        spawn_offset = 1
        while len(self.cars_on_map) < self.config.vehicles["amount"]:
            for vehicle_data in self.config.spawnable_vehicles:
                position_x = self.config.vehicles["first_spawn_x"] * spawn_offset
                position_y = self.config.vehicles["first_spawn_y"]

                new_vehicle = Cars(self.config, position_x, position_y, **vehicle_data)
                self.cars_on_map.append(new_vehicle)
                spawn_offset += 1

                if len(self.cars_on_map) >= self.config.vehicles["amount"]:
                    break

    def reset_manager(self):
        """
        Resets the cars manager.
        :return: None
        """
        self.cars_on_map.clear()
        self.spawn_cars()


class Item:
    """
    Class representing an item.
    :attrib config: The configuration of the game.
    :attrib coordinate_x: The X coordinate.
    :attrib coordinate_y: The Y coordinate.
    :attrib name: The name of the item.
    :attrib texture: The texture of the item.
    :attrib spawn_frequency: The spawn frequency of the item.
    :attrib use_speed: The use speed of the item.
    """
    def __init__(
        self,
        config,
        coordinate_x,
        coordinate_y,
        name,
        texture,
        spawn_frequency,
        use_speed,
    ):
        """
        Initializes the Item class.
        :param config: The configuration of the game.
        :param coordinate_x: The X coordinate.
        :param coordinate_y: The Y coordinate.
        :param name: The name of the item.
        :param texture: The texture of the item.
        :param spawn_frequency: The spawn frequency of the item.
        :param use_speed: The use speed of the item.
        :return: None
        """
        self.config = config
        self.coordinate_x = coordinate_x
        self.coordinate_y = coordinate_y
        self.name = name
        self.texture = texture
        self.spawn_frequency = spawn_frequency
        self.use_speed = use_speed

        self.hitbox = (
            self.coordinate_x,
            self.coordinate_y,
            self.config.items["item_size"],
            self.config.items["item_size"],
        )

        self.last_use_time = 0


class Weapon(Item):
    """
    Class representing a weapon.
    :attrib config: The configuration of the game.
    :attrib coordinate_x: The X coordinate.
    :attrib coordinate_y: The Y coordinate.
    :attrib category: The category of the weapon.
    :attrib name: The name of the weapon.
    :attrib texture: The texture of the weapon.
    :attrib spawn_frequency: The spawn frequency of the weapon.
    :attrib use_speed: The use speed of the weapon.
    :attrib damage: The damage of the weapon.
    :attrib projectile_range: The projectile range of the weapon.
    :attrib explosion_radius: The explosion radius of the weapon.
    """
    def __init__(
        self,
        config,
        coordinate_x,
        coordinate_y,
        category,
        name,
        texture,
        spawn_frequency,
        use_speed,
        damage,
        projectile_range,
        explosion_radius,
    ):
        """
        Initializes the Weapon class.
        :param config: The configuration of the game.
        :param coordinate_x: The X coordinate.
        :param coordinate_y: The Y coordinate.
        :param category: The category of the weapon.
        :param name: The name of the weapon.
        :param texture: The texture of the weapon.
        :param spawn_frequency: The spawn frequency of the weapon.
        :param use_speed: The use speed of the weapon.
        :param damage: The damage of the weapon.
        :param projectile_range: The projectile range of the weapon.
        :param explosion_radius: The explosion radius of the weapon.
        :return: None
        """
        super().__init__(
            config,
            coordinate_x,
            coordinate_y,
            name,
            texture,
            spawn_frequency,
            use_speed,
        )
        self.damage = damage
        self.projectile_range = projectile_range
        self.explosion_radius = explosion_radius
        self.category = category


class Food(Item):
    """
    Class representing food.
    :attrib config: The configuration of the game.
    :attrib coordinate_x: The X coordinate.
    :attrib coordinate_y: The Y coordinate.
    :attrib name: The name of the food.
    :attrib texture: The texture of the food.
    :attrib spawn_frequency: The spawn frequency of the food.
    :attrib use_speed: The use speed of the food.
    :attrib healage: The amount of healing provided by the food.
    """
    def __init__(
        self,
        config,
        coordinate_x,
        coordinate_y,
        name,
        texture,
        spawn_frequency,
        use_speed,
        healage,
    ):
        """
        Initializes the Food class.
        :param config: The configuration of the game.
        :param coordinate_x: The X coordinate.
        :param coordinate_y: The Y coordinate.
        :param name: The name of the food.
        :param texture: The texture of the food.
        :param spawn_frequency: The spawn frequency of the food.
        :param use_speed: The use speed of the food.
        :param healage: The amount of healing provided by the food.
        :return: None
        """
        super().__init__(
            config,
            coordinate_x,
            coordinate_y,
            name,
            texture,
            spawn_frequency,
            use_speed,
        )
        self.healage = healage


class Item_Manager:
    """
    Class responsible for managing items.
    :attrib config: The configuration of the game.
    """
    def __init__(self, config):
        """
        Initializes the Item_Manager class.
        :param config: The configuration of the game.
        :return: None
        """
        self.config = config
        self.items_spawned = []

    def spawn_items(self):
        """
        Spawns items on the map.
        :return: None
        """
        for i in range(self.config.items["item_limit"]):
            rand_x = random.randint(0, self.config.display["map_size"][0])
            rand_y = random.randint(0, self.config.display["map_size"][1])
            roll = random.randint(0, 100)

            for weapon in self.config.spawnable_weapons:
                low, high = weapon["spawn_frequency"]

                if low <= roll <= high:
                    new_item = Weapon(self.config, rand_x, rand_y, **weapon)
                    self.items_spawned.append(new_item)
                    break

    def reset_manager(self):
        """
        Resets the item manager.
        :return: None
        """
        self.items_spawned.clear()
        self.spawn_items()


class Projectile:
    """
    Class representing a projectile.
    :attrib config: The configuration of the game.
    :attrib position_x: The X coordinate.
    :attrib position_y: The Y coordinate.
    :attrib direction_x: The X component of the direction vector.
    :attrib direction_y: The Y component of the direction vector.
    :attrib damage: The damage of the projectile.
    :attrib speed: The speed of the projectile.
    :attrib max_distance: The maximum distance the projectile can travel.
    :attrib texture: The texture of the projectile.
    """
    def __init__(
        self,
        config,
        position_x,
        position_y,
        direction_x,
        direction_y,
        damage,
        speed,
        max_distance,
        texture,
    ):
        """
        Initializes the Projectile class.
        :param config: The configuration of the game.
        :param position_x: The X coordinate.
        :param position_y: The Y coordinate.
        :param direction_x: The X component of the direction vector.
        :param direction_y: The Y component of the direction vector.
        :param damage: The damage of the projectile.
        :param speed: The speed of the projectile.
        :param max_distance: The maximum distance the projectile can travel.
        :param texture: The texture of the projectile.
        :return: None
        """
        self.config = config
        self.position_x = position_x
        self.position_y = position_y
        self.direction_x = direction_x
        self.direction_y = direction_y
        self.damage = damage
        self.speed = speed
        self.max_distance = max_distance
        self.distance_travelled = 0

        self.rect = pygame.Rect(position_x, position_y, 10, 10)

        self.texture = pygame.image.load(texture).convert_alpha()

    def move(self, dt):
        """
        Moves the projectile.
        :param dt: The time passed since the last frame.
        :return: bool
        """
        step_distance = self.speed * dt

        self.position_x += step_distance * self.direction_x
        self.position_y += step_distance * self.direction_y

        self.rect.x = int(self.position_x)
        self.rect.y = int(self.position_y)

        self.distance_travelled += step_distance

        if self.distance_travelled > self.max_distance:
            return False

        return True


class Projectile_Manager:
    """
    Class responsible for managing projectiles.
    :attrib config: The configuration of the game.
    """
    def __init__(self, config):
        """
        Initializes the Projectile_Manager class.
        :param config: The configuration of the game.
        :return: None
        """
        self.bullets_on_map = []
        self.config = config

    def add_projectile(self, projectile):
        """
        Adds a projectile to the map.
        :param projectile: The projectile to add.
        :return: None
        """
        self.bullets_on_map.append(projectile)

    def remove_projectile(self, projectile):
        """
        Removes a projectile from the map.
        :param projectile: The projectile to remove.
        :return: None
        """
        self.bullets_on_map.remove(projectile)

    def move_projectiles(self, dt, enemy_manager, item_manager):
        """
        Moves all active projectiles and handles collisions.
        :param dt: The time passed since the last frame.
        :param enemy_manager: The enemy manager.
        :param item_manager: The item manager.
        :return: None
        """
        for projectile in self.bullets_on_map[:]:
            if projectile.move(dt) is False:
                self.bullets_on_map.remove(projectile)
                continue

            for enemy in enemy_manager.enemies_spawned:
                if projectile.rect.colliderect(enemy.rect) and enemy.hp > 0:
                    enemy.hp -= projectile.damage

                    if enemy.hp <= 0:
                        self.config.current_score += self.config.enemy["points_given"]
                        enemy.death_time = pygame.time.get_ticks()
                        enemy.item_dropper(item_manager)

                    self.remove_projectile(projectile)
                    break


class Inventory:
    """
    Class responsible for managing an inventory.
    :attrib capacity: The capacity of the inventory.
    """
    def __init__(self, capacity=9):
        """
        Initializes the Inventory class.
        :param capacity: The capacity of the inventory.
        :return: None
        """
        self.capacity = capacity
        self.slots: list = [None] * capacity
        self.selected_index = 0

    def add_items(self, item):
        """
        Adds an item to the inventory.
        :param item: The item to add.
        :return: bool
        """
        if self.slots[self.selected_index] is None:
            self.slots[self.selected_index] = item
            return True

        for i in range(len(self.slots)):
            if self.slots[i] is None:
                self.slots[i] = item
                return True
        return False

    def select_slot(self, index):
        """
        Selects an inventory slot.
        :param index: The index of the slot to select.
        :return: None
        """
        if 0 <= index < self.capacity:
            self.selected_index = index

    def scroll(self, direction):
        """
        Scrolls through the inventory slots.
        :param direction: The direction to scroll.
        :return: None
        """
        self.selected_index += direction
        self.selected_index %= self.capacity
