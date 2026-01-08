import pygame
from settings import Config
from model import Player, Item_Manager
from view import View
from controller import Controller


def main():
    pygame.init()

    config = Config()

    screen = pygame.display.set_mode(config.screen_size)

    player = Player(config)
    view = View(screen, config)

    item_manager = Item_Manager(config)
    item_manager.spawn_items()

    controller = Controller(player, view, config, item_manager)


    controller.main_loop()

if __name__ == '__main__':
    main()