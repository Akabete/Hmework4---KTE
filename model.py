import pygame
import random
import math


class Player:
    """
    Represents a player in the game.

    The Player class encapsulates the state and behavior of a player entity. The player
    can move, interact with items, and synchronize with vehicles. It manages its inventory
    and interacts with the game environment while adhering to the configuration settings
    defined during initialization.

    :ivar rect: The rectangular hitbox representing the player's graphical area in the
        game world, defined by its position and dimensions.
    :type rect: Pygame.Rect
    :ivar position_x: The precise x-coordinate of the player in the game world, stored
        as a float for better movement accuracy.
    :type position_x: Float
    :ivar position_y: The precise y-coordinate of the player in the game world, stored
        as a float for better movement accuracy.
    :type position_y: Float
    :ivar hp: The player's health points, representing the amount of damage the player
        can sustain before being incapacitated.
    :type hp: Int
    :ivar speed: The player's default movement speed in the game world, which can
        be influenced by other conditions such as sprinting.
    :type speed: Float
    :ivar sprint_bonus: The additional movement speed applied when the player is
        sprinting.
    :type sprint_bonus: Float
    :ivar inventory: The player's inventory, which manages the storage and selection of
        items the player collects during gameplay.
    :type inventory: Inventory
    :ivar current_vehicle: Represents the currently assigned vehicle the player is
        using, if any; None if the player is not using a vehicle.
    :type current_vehicle: Vehicle or None
    :ivar visible: Boolean indicating whether the player is visible in the game world.
    :type visible: Bool
    """
    def __init__(self, config):
        """
        Initialize the Player instance with configuration settings.

        :param config: The configuration dictionary containing player settings such as
                       spawn location, hitbox dimensions, health points, movement speed,
                       sprint bonus, and other properties.
        :type config: Config
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
        Moves the object based on directional input, sprint status, and elapsed time. Adjusts
        the position of the object and keeps it within the bounds defined by the display map size.

        The movement speed is influenced by the `sprint` parameter, adding a bonus to the current
        speed. Diagonal movement is correctly normalized to avoid excessive speed. The position of
        the object is updated both in float for precision and in integer for rendering purposes.

        The object's position is clamped within the map size to prevent it from moving out of bounds.

        :param direction_x: Horizontal movement direction, where -1 is left, 1 is right, and 0 is no movement
        :type direction_x: int
        :param direction_y: Vertical movement direction, where -1 is up, 1 is down, and 0 is no movement
        :type direction_y: int
        :param sprint: Indicates whether the sprint bonus should be applied
        :type sprint: bool
        :param dt: Delta time representing the time elapsed since the last frame
        :type dt: float
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
        Synchronizes the position of the object with the center of the current vehicle
        if a vehicle is assigned to it. This updates both the graphical representation
        (center of the object's rectangle) and the numerical representation
        (its x and y position).

        :return: None
        """
        if self.current_vehicle is not None:
            self.rect.center = self.current_vehicle.rect.center
            self.position_x = float(self.rect.centerx)
            self.position_y = float(self.rect.centery)

    def item_picker(self, item_manager):
        """
        Checks for collision between the player's rectangle (self.rect) and an item's
        hitbox. If a collision is detected, the item is added to the player's inventory,
        and the item is removed from the item manager's list of spawned items.

        :param item_manager: The manager object responsible for tracking all currently
            spawned items in the game.
        :return: None.
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
        Drops the currently selected item in the inventory to the player's current position
        and adds it to the spawned items managed by `item_manager`.

        This method checks the currently selected inventory slot. If there is an item at the
        selected index, it updates the item's coordinates to match the player's current
        position. The item is then removed from the inventory and added to the list
        of spawned items managed by the `item_manager`.

        :param item_manager: Manages items within the game, specifically the spawning
            and tracking of items in the game world.
        :type item_manager: ItemManager
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
    Represents an enemy character in the game, inherited from the Player class.

    The Enemy class is responsible for managing the behavior, state, and interactions
    of enemy characters within the game. It includes logic for movement, attacking, and
    periodic decision-making to simulate artificial intelligence for the enemy.

    :ivar hp: Health points of the enemy.
    :type hp: Int
    :ivar damage: Damage value the enemy inflicts on the player during an attack.
    :type damage: Int
    :ivar death_time: Tracks the time of the enemy's death for state management.
    :type death_time: Int
    :ivar last_decision_time: Timestamp of the enemy's last directional decision.
    :type last_decision_time: Int
    :ivar last_attack_time: Timestamp when the enemy last performed an attack.
    :type last_attack_time: Int
    :ivar direction: A list representing the movement direction of the enemy in
        terms of x and y axes.
    :type direction: List[float, float]
    :ivar does_sprint: Indicates whether the enemy is currently sprinting.
    :type does_sprint: Bool
    :ivar sprint_bonus: Additional speed value applied when the enemy sprints.
    :type sprint_bonus: Int
    :ivar position_x: Current x-coordinate of the enemy's position.
    :type position_x: Float
    :ivar position_y: Current y-coordinate of the enemy's position.
    :type position_y: Float
    """
    def __init__(self, config, start_x, start_y):
        """
        Initializes an enemy instance with starting configuration, position, and attributes.

        :param config: Configuration data used to initialize the enemy instance.
        :type config: Any
        :param start_x: Initial x-coordinate of the enemy's position.
        :type start_x: Float
        :param start_y: Initial y-coordinate of the enemy's position.
        :type start_y: Float
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
        Determines the behavior of an enemy based on its current health, position, and
        configuration. When the enemy is near the player, it chases the player. Otherwise,
        it periodically changes the direction to wander around.

        :param player: The player object with attributes `position_x` and `position_y`,
                        representing the player's current position.
        :type player: Object
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
        Updates the state of the current object, handling movement and interactions
        such as collisions with the player, including implementing attack logic if
        certain conditions are met. The method will cease to operate if the object's
        health points (hp) are zero or below.

        :param dt: A float value representing the delta time since the last update.
        :param player: The player object, used to check for collisions and apply
            damage when attacking.
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
    Manages the spawning, replacing, and resetting of enemies in the game.

    This class is responsible for handling enemy lifecycle operations, including their creation
    based on the configurations provided, replacement of dead enemies, and resetting of all
    spawned enemies. The enemies are initialized with specified attributes and may be equipped
    with weapons based on predefined probabilities.

    :ivar enemies_spawned: List holding currently active enemy instances managed by this class.
    :type enemies_spawned: List
    :ivar config: Configuration object containing settings for enemy and weapon spawning.
    :type config: Object
    """
    def __init__(self, config):
        """
        Initializes a new instance of the class.

        :param config: Configuration object used to initialize the instance.
        :type config: Object
        """
        self.enemies_spawned = []
        self.config = config

    def spawn_enemies(self):
        """
        Spawns enemies on the map according to the defined configurations. Each enemy is randomly placed
        within the map bounds and may be assigned a weapon based on spawn frequency probabilities.

        The number of enemies spawned is limited by the `enemy["limit"]` configuration. For each enemy,
        the spawn position is determined randomly within the dimensions specified in the `display["map_size"]`
        configuration. Additionally, each enemy may be assigned a weapon in their inventory based on
        predefined spawn frequency values from the `spawnable_weapons` configuration.

        :raises AttributeError: If required attributes are missing in the configurations.
        """
        while len(self.enemies_spawned) < self.config.enemy["limit"]:
            spawn_x = random.randint(0, self.config.display["map_size"][0])
            spawn_y = random.randint(0, self.config.display["map_size"][1])
            enemy = Enemy(self.config, spawn_x, spawn_y)

            roll = random.random()

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
        Removes dead enemies from the active enemy list and spawns new ones if necessary.

        This function iterates through the active enemies and removes those whose health is
        zero or less and whose fade time has elapsed. Once an enemy is removed, a new enemy
        is spawned to maintain the desired number of active enemies.

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
        Resets the enemy manager by clearing the current list of spawned enemies and re-initializing it
        through a new enemy spawning operation.

        :raises None
        :return: None
        """
        self.enemies_spawned.clear()
        self.spawn_enemies()


class Cars:
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
        Initializes a new instance of the class with the specified parameters.

        :param config: Configuration object to initialize the entity.
        :param coordinate_x: X-coordinate of the entity's initial position.
        :param coordinate_y: Y-coordinate of the entity's initial position.
        :param texture: Surface or image object representing the visual
            texture of the entity.
        :param max_speed: The maximum movement speed of the entity.
        :param acceleration: The acceleration value governing movement speed changes.
        :param rotation_speed: Rotation speed of the entity, controlling how fast
            it can rotate.
        :param health: The starting health value for the entity.
        :param hitbox: Tuple defining the width and height of the entity's hitbox.
        :param hiding: Boolean indicating whether the entity is currently hiding.
        :param hitbox_color: Color of the hitbox, used for rendering and diagnostics.
        :param angle: Starting rotation angle of the entity (default is 0).
        :param current_speed: Initial speed of the entity (default is 0).
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
        Calculates and adjusts the acceleration of the entity based on the direction and time
        delta provided. This method updates the current speed of the entity in accordance with
        the maximum speed, acceleration, and friction parameters.

        :param direction_y: Vertical direction control input. A positive value indicates upward
            movement, negative indicates downward movement, and zero means no input.
        :type direction_y: Int or float
        :param dt: Time delta representing the change in time between computations.
        :type dt: Float
        :return: None. The method modifies the object's current speed as a side effect.
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
        Applies physics calculations to update the object's position and rotation based on its
        current speed, direction, and elapsed time.

        :param direction_x: The direction of rotation. Positive values rotate clockwise,
            while negative values rotate counter-clockwise.
        :type direction_x: Float
        :param dt: The change in time (delta time) to calculate positional changes.
            Usually measured in seconds.
        :type dt: Float

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
        Ensures an object's position stays within predefined boundaries. This method checks if the
        object exceeds the map limits on any side (left, right, top, bottom) and adjusts its position
        and speed accordingly, preventing it from moving out of bounds.

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
        Controls the driving behavior of an object by applying physics, acceleration,
        and boundary constraints. This function manages the horizontal and vertical
        movement of the object over a specific time duration.

        :param direction_x: The direction for the horizontal movement.
        :type direction_x: Float
        :param direction_y: The direction for the vertical movement.
        :type direction_y: Float
        :param dt: The time delta representing the elapsed time for the simulation step.
        :type dt: Float
        """
        self._physics(direction_x, dt)
        self._acceleration(direction_y, dt)
        self._boundaries()


class Cars_Manager:
    """
    Manages the behavior and state of cars within a simulated environment.

    This class handles the management of cars on a map. It provides functionality
    to initialize cars, spawn them based on a configuration, and reset the
    entire car management system. The purpose of the class is to ensure that cars
    are handled systematically according to pre-defined rules and limits.

    :ivar config: Configuration object used to control car spawning and behavior.
    :type config: Config
    :ivar cars_on_map: A list of cars currently present on the map.
    :type cars_on_map: List
    """
    def __init__(self, config):
        """
        Initializes the object with a configuration and prepares an empty list
        to store cars on the map.

        :param config: Configuration object to initialize the instance.
        :type config: Config
        """
        self.config = config
        self.cars_on_map = []

    def spawn_cars(self):
        """
        Spawns cars on the map based on the configuration.

        This function manages the spawning of vehicles, adhering to limits defined
        in the configuration. It ensures vehicles are added to the map until the
        desired number of vehicles is reached. Spawn positions are calculated using
        offset values. Newly created vehicles are appended to the internal list
        of cars on the map.

        :raises KeyError: If required keys are missing in the configuration.
        :raises TypeError: If the structure or types in the configuration are incorrect.
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
        Clears the current cars on the map and reinitializes car spawning.

        This method resets the state by clearing all cars currently on the map and then
        invokes the process to spawn new cars.

        :return: None
        """
        self.cars_on_map.clear()
        self.spawn_cars()


class Item:
    """
    Represents an item with specific properties, such as position, appearance,
    behavior, and configuration details.

    This class is designed to model items in an environment, including their spatial
    coordinates, visual representation, spawning behavior, and additional parameters
    important for their functionality.

    :ivar config: Configuration data containing relevant settings and predefined values
        for the item.
    :type config: Any
    :ivar coordinate_x: X-axis position of the item in the environment.
    :type coordinate_x: Int
    :ivar coordinate_y: Y-axis position of the item in the environment.
    :type coordinate_y: Int
    :ivar name: Identifier name for the item.
    :type name: Str
    :ivar texture: Visual texture or representation associated with the item.
    :type texture: Str
    :ivar spawn_frequency: Frequency at which the item spawns in the environment.
    :type spawn_frequency: Float
    :ivar use_speed: Indicates whether the item uses speed mechanics.
    :type use_speed: Bool
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
        Initializes an instance of an object with specified parameters and attributes.
        This includes configuration details, positional coordinates, visual properties,
        spawn characteristics, and behavior flags.

        :param config: Configuration data container holding settings and
            predefined values.
        :type config: Any
        :param coordinate_x: X-axis coordinate position of the object in the
            environment.
        :type coordinate_x: Int
        :param coordinate_y: Y-axis coordinate position of the object in the
            environment.
        :type coordinate_y: Int
        :param name: Name identifier for the object.
        :type name: Str
        :param texture: Visual texture or representation of the object.
        :type texture: Str
        :param spawn_frequency: Rate at which this object is spawned in the
            environment.
        :type spawn_frequency: Float
        :param use_speed: Flag indicating whether this object uses speed
            settings or mechanics.
        :type use_speed: Bool
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
    Represents a weapon in the game, inherited from `Item`.

    This class is designed to add specific properties and behaviors of a weapon to
    an object. Weapons are categorized with unique attributes such as damage, range,
    and explosion radius in addition to the attributes inherited from the parent class.

    :ivar damage: The amount of damage the weapon can cause.
    :type damage: Int
    :ivar projectile_range: The maximum distance the projectile from the weapon can travel.
    :type projectile_range: Int
    :ivar explosion_radius: The radius of the explosion caused by the weapon, if applicable.
    :type explosion_radius: Int
    :ivar category: The classification or type of the weapon.
    :type category: Str
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
        Initializes an instance of the class with the given parameters.

        The class inherits from another superclass and adds additional attributes
        to define specific characteristics such as damage, range, and explosion
        radius. Each parameter is used to initialize the corresponding attributes
        necessary for the behavior and properties of the class.

        :param config: Configuration object required for initialization.
        :param coordinate_x: The X-coordinate indicating the position of the object.
        :param coordinate_y: The Y-coordinate indicating the position of the object.
        :param category: Category or classification of the object.
        :param name: Name of the object.
        :param texture: Texture or appearance data for the object.
        :param spawn_frequency: The frequency at which the object spawns.
        :param use_speed: Speed attribute for the object's usage or movement.
        :param damage: Amount of damage the object can cause.
        :param projectile_range: The range of the object's projectile.
        :param explosion_radius: The radius of the explosion caused by the object.
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
    Represents a food item in the game system.

    The Food class inherits from the Item class and adds the ability to
    store information about the healing power of the food. This class is
    designed to manage food-specific attributes and serve as a base for
    operations involving food objects.

    :ivar healage: The amount of healing power the food provides.
    :type healage: Int
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
        Initializes an instance of the class with the given parameters, extending the
        parent initialization process by including the healage attribute.

        :param config: Game configuration object used for initialization.
        :param coordinate_x: Initial x-coordinate of the object.
        :param coordinate_y: Initial y-coordinate of the object.
        :param name: Name identifier for the object.
        :param texture: Texture information for rendering the object.
        :param spawn_frequency: Frequency at which this object spawns in the game.
        :param use_speed: Boolean flag indicating whether speed is applicable.
        :param healage: Healing value or amount associated with the object.
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
    Manages item spawning in the game environment.

    This class handles the spawning and tracking of items within the game's map.
    It works based on the provided configuration data, enabling dynamic creation
    of items such as weapons with specific spawning probabilities and conditions.

    :ivar config: Configuration object containing spawn constraints, item data, and map settings.
    :type config: Any
    :ivar items_spawned: List to keep track of all items spawned on the map.
    :type items_spawned: List
    """
    def __init__(self, config):
        """
        Represents the main class responsible for initial setup and managing spawned items.

        This class is initialized with a `config` object and maintains a collection
        of items that have been spawned. It is designed for the basic handling of
        initial configurations and spawned items tracking.

        :param config: Represents the configuration used during initialization.

        :ivar config: The configuration object passed during initialization.
        :attribute items_spawned: A list of items that have been spawned.
        """
        self.config = config
        self.items_spawned = []

    def spawn_items(self):
        """
        Spawns items on the map based on configuration probabilities and constraints.

        This method iterates through the number of items defined in the configuration
        to spawn. It calculates a random position for each item within the map boundaries
        and assigns a random probability value. Based on the probability, the method
        determines which weapon should be spawned and generates the corresponding weapon
        object. The spawned items are then appended to the spawn list.

        :raises ValueError: If any issue occurs with weapon data or configuration.
        :return: None
        """
        for i in range(self.config.items["item_limit"]):
            rand_x = random.randint(0, self.config.display["map_size"][0])
            rand_y = random.randint(0, self.config.display["map_size"][1])
            roll = random.random()

            for weapon in self.config.spawnable_weapons:
                low, high = weapon["spawn_frequency"]

                if low <= roll <= high:
                    new_item = Weapon(self.config, rand_x, rand_y, **weapon)
                    self.items_spawned.append(new_item)
                    break

    def reset_manager(self):
        """
        Clears the list of spawned items and initializes the spawning of new items.

        This method first resets the internal tracking of spawned items and
        then proceeds to spawn new items as defined by the application logic.

        :raises RuntimeError: If spawning items fails due to an internal issue.
        :return: None
        """
        self.items_spawned.clear()
        self.spawn_items()


class Projectile:
    """
    Represents a projectile in a 2D space within a game.

    The Projectile class is responsible for modeling a moving projectile with attributes
    such as position, direction, speed, damage, range, and visual representation. It
    provides functionality to update the position of the projectile and tracks the distance
    it travels, ensuring it adheres to its defined range.

    :ivar config: Configuration object containing game-specific settings.
    :type config: Any
    :ivar position_x: Initial X-coordinate of the projectile.
    :type position_x: Float
    :ivar position_y: Initial Y-coordinate of the projectile.
    :type position_y: Float
    :ivar direction_x: X component of the projectile's direction vector.
    :type direction_x: Float
    :ivar direction_y: Y component of the projectile's direction vector.
    :type direction_y: Float
    :ivar damage: Damage value inflicted by the projectile.
    :type damage: Int
    :ivar speed: Movement speed of the projectile.
    :type speed: Float
    :ivar max_distance: Maximum travel distance of the projectile.
    :type max_distance: Float
    :ivar distance_travelled: Cumulative distance the projectile has traveled.
    :type distance_travelled: Float
    :ivar rect: Pygame rectangle representing the projectile's rendering area.
    :type rect: Pygame.Rect
    :ivar texture: Visual representation of the projectile loaded as an image.
    :type texture: Pygame.Surface
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
        Constructor for initializing the projectile object.

        This class method initializes all the necessary properties of the projectile,
        such as its position, direction, damage, speed, range, and visual appearance
        (texture). The method also sets up a Pygame rectangle to define the projectile's
        rendering space and keeps track of the total distance traveled by the projectile.

        :param config: Configuration object containing game-specific settings.
        :param position_x: X-coordinate of the projectile's starting position.
        :param position_y: Y-coordinate of the projectile's starting position.
        :param direction_x: X component of the projectile's direction vector.
        :param direction_y: Y component of the projectile's direction vector.
        :param damage: Amount of damage caused by the projectile.
        :param speed: Speed of the projectile.
        :param max_distance: Maximum distance the projectile can travel.
        :param texture: Path to the texture/image file for the appearance of the projectile.
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
        Updates the position of the object based on its current speed, direction, and the time
        delta. Adjusts the position of the object's rectangle, tracks the distance traveled,
        and checks if the object has exceeded its movement range.

        :param dt: The time delta used to calculate the movement distance
        :type dt: float
        :return: True if the object is still within its movement range, False otherwise
        :rtype: bool
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
    Manages and controls the behavior of projectiles present on the map.

    This class is responsible for adding and removing projectiles, moving them across
    the game environment, interacting with enemies, and handling collision events.
    It interacts with external managers for enemies and items to ensure that all
    game elements are synchronized and updated as needed.

    :ivar bullets_on_map: A list that keeps track of all projectiles currently present
        on the map.
    :type bullets_on_map: List
    :ivar config: A configuration object containing settings and parameters necessary
        for managing projectiles and their interactions.
    :type config: Config
    """
    def __init__(self, config):
        """
        Initializes an instance of the class.

        :param config: Configuration object for initializing the class
        :type config: Config
        """
        self.bullets_on_map = []
        self.config = config

    def add_projectile(self, projectile):
        """
        Adds a projectile to the list of bullets on the map.

        This method appends a given projectile to the internal list that tracks
        all the current bullets on the map.

        :param projectile: The projectile object to be added to the list.
        :return: None
        """
        self.bullets_on_map.append(projectile)

    def remove_projectile(self, projectile):
        """
        Removes a specified projectile from the collection of bullets available
        on the map. This method is commonly used to clean up projectiles
        that are no longer needed, such as after a collision or when they
        exit the map.

        :param projectile: The projectile object to be removed from the map.
        :type projectile: Any
        :return: None
        """
        self.bullets_on_map.remove(projectile)

    def move_projectiles(self, dt, enemy_manager, item_manager):
        """
        Handles the projectiles' movements, checks for collisions with enemies, updates
        the state of enemies, and manages the removal of projectiles.

        :param dt: A float value representing the time elapsed since the last update,
            used to calculate projectile movement.
        :param enemy_manager: An object responsible for managing spawned enemies,
            providing access to the list of active enemies.
        :param item_manager: An object responsible for managing item drops upon
            enemy death.
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
    Represents an inventory system with fixed capacity, allowing items to be added,
    slots to be selected, and the current selection to be scrolled.

    The purpose of this class is to provide a structure for managing items in
    a fixed number of slots where only one slot can be active (selected) at a time.

    :ivar capacity: The total number of slots the inventory can hold.
    :type capacity: Int
    :ivar slots: A list representing the slots in the inventory, initially set to None.
    :type slots: List
    :ivar selected_index: The index of the currently selected slot in the inventory.
    :type selected_index: Int
    """
    def __init__(self, capacity=9):
        """
        Initializes an object with a fixed number of slots, where items can be held,
        and a selected index marking the current active position.

        The `capacity` parameter defines the total number of slots available, and
        the slots are initialized as empty (represented by `None`).

        :param capacity: Total number of slots available to be occupied
        :type capacity: int
        """
        self.capacity = capacity
        self.slots: list = [None] * capacity
        self.selected_index = 0

    def add_items(self, item):
        """
        Adds an item to the first available slot in the inventory.

        If the currently selected slot is empty, the item is added there. If the
        selected slot is not empty, the function searches for the next empty slot
        and places the item there. If no empty slot is available, the item is not
        added.

        :param item: The item to be added to the inventory.
        :type item: Any
        :return: True if the item is successfully added, False otherwise.
        :rtype: Bool
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
        Select a slot based on the given index. Updates the selected index if the
        index is within valid bounds (0 to capacity - 1).

        :param index: The index of the slot to select
        :type index: int
        :return: None
        """
        if 0 <= index < self.capacity:
            self.selected_index = index

    def scroll(self, direction):
        """
        Scrolls the selection index in the given direction, ensuring the index remains
        within bounds by using modulo operation.

        :param direction: The integer value indicating the direction of scrolling.
                          Positive values scroll forward, negative values scroll
                          backward.
        :return: None
        """
        self.selected_index += direction
        self.selected_index %= self.capacity
