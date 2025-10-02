import os
import sys

from structures import *


def resource_path(relative_path: str) -> str:
    """Возвращает путь к ресурсу (для dev и exe)."""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def init():
    pygame.init()
    screen = pygame.display.set_mode(width_height)
    pygame.display.set_caption(window_name)
    clock = time.Clock()
    world_map = Map(text_map, screen, blocks_setting, base_block_size)
    player = Player(screen, pygame.Rect(0, 0, player_width, player_width), player_speed, keys, player_color,
                    [player_height, player_width], world_map.map)
    player.figure.center = center
    textures = {"W": pygame.image.load(resource_path('img/1.png')).convert(),
                "B": pygame.image.load(resource_path('img/2.png')).convert(),
                "S": pygame.image.load(resource_path('img/sky.png')).convert()}
    drawing = Drawing(screen, pygame.font.SysFont('Arial', 36, bold=True), textures)
    trigo_cache = numba.typed.Dict.empty(key_type=numba.types.float32,
                                         value_type=numba.types.UniTuple(numba.types.float32, 2))
    return player, clock, world_map, drawing, trigo_cache


def main(player, clock, world_map, drawing, trigo_cache):
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        player.movement(pygame.key.get_pressed())
        drawing.back_ground(player.angle)
        drawing.world(player.figure.x, player.figure.y, player.angle, world_map.map, trigo_cache)
        # Рисуем объекты, обновляем экран
        world_map.draw()
        player.draw()
        drawing.fps(clock)
        pygame.display.update()

        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    main(*init())
