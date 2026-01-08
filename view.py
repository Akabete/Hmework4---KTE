import pygame
from pygame import Color


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
                item_texture = pygame.image.load(inventory_item).convert_alpha()

                self.screen.blit(item_texture,(slot_rect.x, slot_rect.y))
