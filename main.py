import pygame
from settings import Config
from model import Player
from view import View
from controller import Controller


def main():
    pygame.init()

    config = Config()

    screen = pygame.display.set_mode(config.screen_size)

    player = Player(config)
    view = View(screen, config)

    controller = Controller(player, view, config)

    controller.main_loop()


if __name__ == '__main__':
    main()