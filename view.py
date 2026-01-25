import pygame
from pygame import Color
import math, random


class View:
    def __init__(self, screen, config, projectile_manager, cars_manager):
        self.screen = screen
        self.config = config
        self.projectile_manager = projectile_manager
        self.cars_manager = cars_manager
        self.textures = {}
        self.hand_textures = {}

        for weapon_data in self.config.spawnable_weapons:
            path =  weapon_data["texture"]
            full_sprite = pygame.image.load(path).convert_alpha()
            self.textures[path] = full_sprite

            size = self.config.items["item_size_in_hand"]
            self.hand_textures[path] = pygame.transform.scale(full_sprite, (size, size))

        self.map_surface = pygame.Surface(self.config.display["map_size"]).convert()
        map_texture = pygame.image.load(self.config.display["map_texture"]).convert()

        map_texture_image = pygame.transform.scale(map_texture, self.config.display["map_size"])
        self.map_surface.blit(map_texture_image, (0, 0))


    def get_camera_rect(self, player):
        target_x = player.centerx - (self.config.display["screen_size"][0] / 2)
        target_y = player.centery - (self.config.display["screen_size"][1] / 2)

        limit_x = self.config.display["map_size"][0] - self.config.display["screen_size"][0]
        limit_y = self.config.display["map_size"][1] - self.config.display["screen_size"][1]

        final_x = max(0, min(target_x, limit_x))
        final_y = max(0, min(target_y, limit_y))

        return pygame.Rect(final_x, final_y, self.config.display["map_size"][0], self.config.display["map_size"][1])

    @staticmethod
    def world_to_screen(world_position, camera_rect):
        screen_x = world_position[0] - camera_rect.x
        screen_y = world_position[1] - camera_rect.y
        return screen_x, screen_y


    def _draw_player(self, player_model, camera_rect):
        if player_model.visible:
            screen_position = self.world_to_screen(player_model.rect.topleft, camera_rect)
            player_screen_rect = pygame.Rect(screen_position, player_model.rect.size)

            pygame.draw.rect(self.screen, self.config.player["texture"], player_screen_rect)
            return player_screen_rect
        return None

    def _draw_enemies(self, enemy_manager, camera_rect):
        current_time = pygame.time.get_ticks()

        for enemy in enemy_manager.enemies_spawned:
            screen_position = self.world_to_screen(enemy.rect.topleft, camera_rect)
            enemy_screen_rect = pygame.Rect(screen_position, enemy.rect.size)

            if enemy.hp <= 0:
                self._draw_dead_enemy(enemy, enemy_screen_rect, current_time)
            else:
                pygame.draw.rect(self.screen, self.config.enemy["texture"], enemy_screen_rect)

    def _draw_dead_enemy(self, enemy, screen_rect, current_time):
        time_passed = current_time - enemy.death_time

        fade_ratio = time_passed / self.config.enemy["fade_time"]
        alpha = max(0, 255 - int(fade_ratio * 255))

        # 3. Create the surface and apply transparency
        enemy_surface = pygame.Surface(enemy.rect.size).convert_alpha()
        enemy_surface.fill(self.config.enemy["texture"])
        enemy_surface.set_alpha(alpha)

        self.screen.blit(enemy_surface, screen_rect)


    def _draw_ground_items(self, item_manager, camera_rect):
        for item in item_manager.items_spawned:
            item_position = item.coordinate_x, item.coordinate_y
            screen_position = self.world_to_screen(item_position, camera_rect)

            self.screen.blit(self.textures[item.texture], screen_position)


    def _draw_vehicles(self, camera_rect):
        for vehicle in self.cars_manager.cars_on_map:
            screen_position = self.world_to_screen(vehicle.rect.topleft, camera_rect)
            car_screen_rect = pygame.Rect(screen_position, vehicle.rect.size)

            pygame.draw.rect(self.screen, vehicle.texture, car_screen_rect)


    def _draw_projectiles(self, camera_rect):
        for projectile in self.projectile_manager.bullets_on_map:
            world_position = projectile.position_x, projectile.position_y
            screen_position = self.world_to_screen(world_position, camera_rect)

            self.screen.blit(projectile.texture, screen_position)


    def _get_item_offset(self, item, time_passed, dx):
        if time_passed > item.use_speed: return 0

        progress = time_passed / item.use_speed
        sin_value = math.sin(progress * math.pi)
        strength = self.config.combat["swing_strength"]
        recoil = self.config.combat["recoil_strength"]

        if "melee" in item.category or "throwable" in item.category:
            return -sin_value * strength if dx > 0 else sin_value * strength
        elif "special" in item.category:
            return random.randint(-3, 3) if time_passed < 100 else 0
        else:
            return sin_value * recoil if dx > 0 else -sin_value * recoil


    def _draw_rotated_item(self, item, angle, angle_deg, dx, player_rect):
        sprite = self.hand_textures[item.texture]
        if dx < 0:
            sprite = pygame.transform.flip(sprite, False, True)

        rotated_sprite = pygame.transform.rotate(sprite, angle_deg)

        distance = self.config.combat["hand_distance"]
        offset_x = math.cos(angle) * distance
        offset_y = math.sin(angle) * distance

        target_position = player_rect.centerx + offset_x, player_rect.centery + offset_y

        rect = rotated_sprite.get_rect()
        if dx > 0:
            rect.midleft = target_position
        else:
            rect.midright = target_position

        self.screen.blit(rotated_sprite, rect)


    def _draw_held_item(self, player_model, player_screen_rect):
        if player_screen_rect is not None:
            active_item = player_model.inventory.slots[player_model.inventory.selected_index]
            if active_item is not None:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                px, py = player_screen_rect.center
                dx, dy = mouse_x - px, mouse_y - py

                angle = math.atan2(dy, dx)
                angle_deg = -math.degrees(angle)

                time_passed = pygame.time.get_ticks() - active_item.last_use_time
                angle_deg += self._get_item_offset(active_item, time_passed, dx)

                self._draw_rotated_item(active_item, angle, angle_deg, dx, player_screen_rect)


    def draw_inventory(self, player_model):
        inventory = player_model.inventory
        start_x = 5
        start_y = 5
        columns = 3

        for i in range(inventory.capacity):
            row = i // columns
            column = i % columns
            slot_x = start_x + (column * self.config.items["slot_size"] + (column * self.config.items["inventory_gap"]) - 1)
            slot_y = start_y + (row * self.config.items["slot_size"] + (row * self.config.items["inventory_gap"]) - 1)
            slot_rect = pygame.Rect(slot_x, slot_y, self.config.items["slot_size"], self.config.items["slot_size"])

            if i == inventory.selected_index:
                color = Color(0, 0, 255, 128)
                width = 10
            else:
                color = "dark gray"
                width = 5

            pygame.draw.rect(self.screen, color, slot_rect, width)

            if inventory.slots[i] is not None:
                inventory_item = inventory.slots[i].texture
                item_texture = self.textures[inventory_item]

                self.screen.blit(item_texture, (slot_rect.x, slot_rect.y))


    def draw_world(self, player_model, item_manager, enemy_manager):
        camera_rect = self.get_camera_rect(player_model.rect)

        self.screen.fill("black")
        self.screen.blit(self.map_surface, (0, 0), camera_rect)

        self._draw_ground_items(item_manager, camera_rect)
        self._draw_vehicles(camera_rect)
        player_screen_rect = self._draw_player(player_model, camera_rect)
        self._draw_enemies(enemy_manager, camera_rect)
        self._draw_projectiles(camera_rect)

        self._draw_held_item(player_model, player_screen_rect)
        self.draw_inventory(player_model)

        pygame.display.flip()


    def draw_text(self, text, size, position_x, position_y, color):
        font = pygame.font.Font(self.config.display["font"], size)
        text = font.render(text, True, color)
        self.screen.blit(text, (position_x - text.get_width() // 2, position_y))


    def draw_menu(self, title, subtitle):
        self.screen.fill("black")

        center_x = self.config.display["screen_size"][0] // 2
        self.draw_text(title, 72, center_x, 200, "red" if title == "WASTED" else "white")
        self.draw_text(subtitle, 36, center_x, 350, "white")

        pygame.display.flip()
