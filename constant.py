import pygame
import math
import numpy as np

width_height = np.array([1920, 1080], dtype=np.int16)
half_height = width_height[1] // 2
center = width_height // 2
window_name = "Game"

keys = {"up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d,
        "left_angle": pygame.K_LEFT, "right_angle": pygame.K_RIGHT}
player_width, player_height = 20, 20
player_color = "red"
player_speed = 4

fps = 100

text_map = ["WWWWWWWWWWWWWWWWW",
            "W...............W",
            "W...............W",
            "W....BBBBBB.....W",
            "W....B.BB.B.....W",
            "W....B....B.....W",
            "W....BB..BB.....W",
            "W...............W",
            "W...............W",
            "W...............W",
            "W...............W",
            "W...............W",
            "WWWWWWWWWWWWWWWWW", ]

base_block_size = 100
blocks_setting = {"W": (base_block_size, "blue"),
                  "B": (base_block_size, "brown")}

fov = math.pi / 3
half_fov = fov / 2
num_rays = 480
delta_angle = fov / num_rays
dist = num_rays / (2 * math.tan(half_fov))
proj_c = dist * base_block_size*3
scale = width_height[0] // num_rays

pi_2 = np.float32(np.pi/ 2)
pix2 = round(math.pi * 2, 1)
texture_width = 1000
texture_height = 1000
half_texture_height = texture_height // 2
texture_scale = texture_width // base_block_size

proc_size = width_height[0] // 10, width_height[1]
