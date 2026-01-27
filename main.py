import pygame
from settings import Config
from model import Player, Item_Manager, Enemy_Manager, Projectile_Manager, Cars_Manager
from view import View
from controller import Controller


def main():
    pygame.init()

    config = Config()

    screen = pygame.display.set_mode(config.display["screen_size"])

    player = Player(config)

    enemy_manager = Enemy_Manager(config)
    enemy_manager.spawn_enemies()

    item_manager = Item_Manager(config)
    item_manager.spawn_items()

    projectile_manager = Projectile_Manager(config)

    cars_manager = Cars_Manager(config)

    view = View(screen, config, projectile_manager, cars_manager)

    controller = Controller(player, view, config, item_manager,
                            enemy_manager, projectile_manager, cars_manager)

    controller.main_loop()


if __name__ == '__main__':
    main()
