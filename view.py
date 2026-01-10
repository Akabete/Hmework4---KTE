import pygame
from pygame import Color
import math


class View:
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config
        self.textures = {
            self.config.melee_texture: pygame.image.load(self.config.melee_texture).convert_alpha(),
            self.config.pistol_texture: pygame.image.load(self.config.pistol_texture).convert_alpha(),
            self.config.rifle_texture: pygame.image.load(self.config.rifle_texture).convert_alpha(),
            self.config.special_texture: pygame.image.load(self.config.special_texture).convert_alpha(),
            self.config.throwable_texture: pygame.image.load(self.config.throwable_texture).convert_alpha()

        }
        self.hand_textures = {
            self.config.melee_texture: pygame.transform.scale(pygame.image.load(self.config.melee_texture).convert_alpha(),
                                                        (self.config.item_in_hand_size, self.config.item_in_hand_size)),
            self.config.pistol_texture: pygame.transform.scale(pygame.image.load(self.config.pistol_texture).convert_alpha(),
                                                        (self.config.item_in_hand_size, self.config.item_in_hand_size)),
            self.config.rifle_texture: pygame.transform.scale(pygame.image.load(self.config.rifle_texture).convert_alpha(),
                                                        (self.config.item_in_hand_size, self.config.item_in_hand_size)),
            self.config.special_texture: pygame.transform.scale(pygame.image.load(self.config.special_texture).convert_alpha(),
                                                        (self.config.item_in_hand_size, self.config.item_in_hand_size)),
            self.config.throwable_texture: pygame.transform.scale(pygame.image.load(self.config.throwable_texture).convert_alpha(),
                                                        (self.config.item_in_hand_size, self.config.item_in_hand_size)),

        }

        self.map_surface = pygame.Surface(self.config.map_size).convert()
        map_texture = pygame.image.load(self.config.map_texture).convert()

        map_texture_image = pygame.transform.scale(map_texture, self.config.map_size)
        self.map_surface.blit(map_texture_image, (0, 0))

        for x in range(0, config.map_size[0], 100):
            pygame.draw.line(self.map_surface, (100, 100, 100), (x, 0), (x, config.map_size[1]))
            pygame.draw.line(self.map_surface, (100, 100, 100), (0, x), (config.map_size[0], x))

    def draw_world(self, player_model, item_manager):

        camera_x = player_model.rect.centerx - (self.config.screen_size[0] / 2)
        camera_y = player_model.rect.centery - (self.config.screen_size[1] / 2)

        if camera_x < 0:
            camera_x = 0
        elif camera_x > self.config.map_size[0] - self.config.screen_size[0]:
            camera_x = self.config.map_size[0] - self.config.screen_size[0]

        if camera_y < 0:
            camera_y = 0
        elif camera_y > self.config.map_size[1] - self.config.screen_size[1]:
            camera_y = self.config.map_size[1] - self.config.screen_size[1]

        visible_area_rect = pygame.Rect(
            camera_x,
            camera_y,
            self.config.screen_size[0],
            self.config.screen_size[1]
        )

        self.screen.fill("black")
        self.screen.blit(self.map_surface, (0, 0), visible_area_rect)

        player_screen_rect = player_model.rect.copy()

        player_screen_rect.x = player_model.rect.x - camera_x
        player_screen_rect.y = player_model.rect.y - camera_y

        pygame.draw.rect(self.screen, self.config.player_color, player_screen_rect)

        self.draw_inventory(player_model)


        for item in item_manager.items_spawned:
            screen_x = item.coordinate_x - camera_x
            screen_y = item.coordinate_y - camera_y

            self.screen.blit(self.textures[item.texture],( screen_x, screen_y))

        active_item = player_model.inventory.slots[player_model.inventory.selected_index]

        if active_item is not None:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            player_x, player_y = player_screen_rect.center

            dx = mouse_x - player_x
            dy = mouse_y - player_y

            angle = math.atan2(dy, dx)
            angle_degrees = -math.degrees(angle)

            active_sprite = self.hand_textures[active_item.texture]

            if dx < 0:
                active_sprite = pygame.transform.flip(active_sprite, False, True)

            rotated_item = pygame.transform.rotate(active_sprite, angle_degrees)

            circle_x = math.cos(angle) * 30
            circle_y = math.sin(angle) * 30

            new_rect = rotated_item.get_rect()

            item_position_x = player_screen_rect.centerx + circle_x
            item_position_y = player_screen_rect.centery + circle_y

            new_rect.center = item_position_x, item_position_y

            self.screen.blit(rotated_item, new_rect)




        pygame.display.flip()

    def draw_inventory(self, player_model):
        inventory = player_model.inventory
#        total_width = (inventory.capacity * self.config.inventory_slot) + ((inventory.capacity - 1) * self.config.inventory_gap)

        start_x = 5
        start_y = 5
        columns = 3

        for i in range(inventory.capacity):
            row = i // columns
            column = i % columns
            slot_x = start_x + (column * self.config.inventory_slot + (column * self.config.inventory_gap) - 1)
            slot_y = start_y + (row * self.config.inventory_slot + (row * self.config.inventory_gap) - 1)

            slot_rect = pygame.Rect(slot_x, slot_y, self.config.inventory_slot, self.config.inventory_slot)

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

                self.screen.blit(item_texture,(slot_rect.x, slot_rect.y))
