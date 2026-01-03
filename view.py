import pygame

class View:
    def __init__(self, screen, config):
        self.screen = screen
        self.config = config

        self.map_surface = pygame.Surface(self.config.map_size)
        map_texture = pygame.image.load(self.config.map_texture)

        map_texture_image = pygame.transform.scale(map_texture, self.config.map_size)
        self.map_surface.blit(map_texture_image, (0, 0))

        for x in range(0, config.map_size[0], 100):
            pygame.draw.line(self.map_surface, (100, 100, 100), (x, 0), (x, config.map_size[1]))
            pygame.draw.line(self.map_surface, (100, 100, 100), (0, x), (config.map_size[0], x))

    def draw_world(self, player_model):

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

        self.screen.fill("black")
        self.screen.blit(self.map_surface, (-camera_x, -camera_y))

        player_screen_rect = player_model.rect.copy()

        player_screen_rect.x = player_model.rect.x - camera_x
        player_screen_rect.y = player_model.rect.y - camera_y

        pygame.draw.rect(self.screen, self.config.player_color, player_screen_rect)

        pygame.display.flip()