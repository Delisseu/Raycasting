import dataclasses

from pygame import draw, Surface, font, Rect, time

from ray_casting import *


@dataclasses.dataclass
class Player:
    screen: Surface
    figure: Rect
    speed: float
    keys: dict
    color: str | list | tuple
    size: list | tuple
    angle = np.float32(0)
    map: numba.typed.Dict
    hor: int = dataclasses.field(init=False)
    vert: int = dataclasses.field(init=False)

    def __post_init__(self):
        self.hor = self.size[0] // 2
        self.vert = self.size[1] // 2

    def movement(self, window_keys):
        if window_keys[self.keys['up']]:
            self.forward()
        if window_keys[self.keys['down']]:
            self.backward()
        if window_keys[self.keys['left']]:
            self.left()
        if window_keys[self.keys['right']]:
            self.right()
        if window_keys[self.keys['left_angle']]:
            self.left_angle()
        if window_keys[self.keys['right_angle']]:
            self.right_angle()
        if self.angle >= np.float32(pix2):
            self.angle = np.float32(0)
        elif self.angle < np.float32(0):
            self.angle = np.float32(pix2)

    def update(self, new_x, new_y):
        if not self.check_collision(new_x, new_y):
            self.figure.x = new_x
            self.figure.y = new_y

    def forward(self):
        new_x = np.float32(self.figure.x) + self.speed * np.cos(self.angle)
        new_y = np.float32(self.figure.y) + self.speed * np.sin(self.angle)
        self.update(new_x, new_y)

    def backward(self):
        new_x = np.float32(self.figure.x) - self.speed * np.cos(self.angle, dtype=np.float32)
        new_y = np.float32(self.figure.y) - self.speed * np.sin(self.angle, dtype=np.float32)
        self.update(new_x, new_y)

    def left(self):
        new_x = np.float32(self.figure.x) + self.speed * np.cos(self.angle - pi_2, dtype=np.float32)
        new_y = np.float32(self.figure.y) + self.speed * np.sin(self.angle - pi_2, dtype=np.float32)
        self.update(new_x, new_y)

    def right(self):
        new_x = np.float32(self.figure.x) + self.speed * np.cos(self.angle + pi_2, dtype=np.float32)
        new_y = np.float32(self.figure.y) + self.speed * np.sin(self.angle + pi_2, dtype=np.float32)
        self.update(new_x, new_y)

    def left_angle(self):
        self.angle = np.round(self.angle - np.float32(0.1), 1).astype(np.float32)

    def right_angle(self):
        self.angle = np.round(self.angle + np.float32(0.1), 1).astype(np.float32)

    def draw(self):
        draw.circle(self.screen, self.color, (self.figure.x // 5, self.figure.y // 5), sum(self.size) // 4)
        draw.line(self.screen, self.color, (self.figure.x // 5, self.figure.y // 5),
                  (self.figure.x // 5 + int(20 * np.cos(self.angle, dtype=np.float32)),
                   self.figure.y // 5 + int(20 * np.sin(self.angle, dtype=np.float32))))

    def check_collision(self, new_x, new_y):
        # Проверка коллизии для нескольких точек вокруг игрока (например, для его углов)
        points_to_check = [
            (new_x, new_y),  # Центр игрока
            (new_x - self.hor, new_y),  # Левый край
            (new_x + self.hor, new_y),  # Правый край
            (new_x, new_y - self.vert),  # Верхний край
            (new_x, new_y + self.vert)  # Нижний край
        ]

        for px, py in points_to_check:
            px, py = mapping(px, py)
            if (px, py) in self.map:
                return True  # Столкновение
        return False  # Нет столкновения


@dataclasses.dataclass
class Drawing:
    screen: Surface
    font: font
    textures: dict

    def back_ground(self, angle):
        self.screen.fill((0, 0, 0))
        sky_offset = -20 * np.degrees(angle, dtype=np.float32) % width_height[0]
        sky = self.textures['S']
        self.screen.blit(sky, (int(sky_offset), 0))
        self.screen.blit(sky, (int(sky_offset - width_height[0]), 0))
        self.screen.blit(sky, (int(sky_offset + width_height[0]), 0))
        draw.rect(self.screen, (40, 40, 40), (0, half_height, width_height[0], half_height))

    def fps(self, clock):
        display_fps = str(int(clock.get_fps()))
        render = self.font.render(display_fps, 0, "red")
        self.screen.blit(render, (width_height[0] - 65, 5))

    def world(self, x, y, angle, world_map, trigo_cache):
        for x, y, z, h in ray_casting(x, y, angle, world_map, trigo_cache):
            wall_column = self.textures[x[0]].subsurface(*y)
            wall_column = pygame.transform.scale(wall_column, z)
            self.screen.blit(wall_column, h)


@dataclasses.dataclass
class Map:
    text_map: list
    screen: Surface
    blocks_setting: dict
    base_block_size: int
    map: numba.typed.Dict = dataclasses.field(init=False)
    mini_map: dict = dataclasses.field(init=False)

    def __post_init__(self):
        self.map, self.mini_map = self.update_map()

    def update_map(self):
        world_map = numba.typed.Dict.empty(key_type=numba.types.UniTuple(numba.types.float32, 2),
                                           value_type=numba.types.Tuple(
                                               (numba.types.string, numba.types.float32, numba.types.string)))
        mini_map = dict()
        for i, row in enumerate(self.text_map):
            for j, char in enumerate(row):
                curr_setting = self.blocks_setting.get(char)
                if curr_setting:
                    x, y = j * self.base_block_size, i * self.base_block_size
                    world_map[(x, y)] = (char, *curr_setting)
                    mini_map[(j * (self.base_block_size // 5), i * (self.base_block_size // 5))] = curr_setting
        return world_map, mini_map

    def draw(self):
        draw.rect(self.screen, 'black',
                  (0, 0, len(max(text_map)) * base_block_size // 5, len(text_map) * base_block_size // 5))
        for x, y in self.mini_map.items():
            draw.rect(self.screen, y[1], (*x, self.base_block_size / 5, self.base_block_size / 5))
