import numba
from numba.core.errors import NumbaTypeSafetyWarning
import warnings
warnings.filterwarnings("ignore", category=NumbaTypeSafetyWarning)
from constant import *


@numba.njit(fastmath=True)
def mapping(a, b):
    return (a // base_block_size) * base_block_size, (b // base_block_size) * base_block_size


@numba.njit(fastmath=True)
def trigo(curr_angle, trigo_cache):
    res = trigo_cache.get(curr_angle, default=None)
    if res is None:
        res = (np.sin(np.float32(curr_angle)), np.cos(np.float32(curr_angle)))
        trigo_cache[curr_angle] = res
    return res


@numba.njit(fastmath=True)
def ray_casting(x, y, player_angle, world_map, trigo_cache):
    curr_angle = player_angle - half_fov
    xo, yo = x, y
    xm, ym = mapping(xo, yo)
    list_of_rays = []
    xm_block_size = xm + base_block_size
    ym_block_size = ym + base_block_size
    for ray in range(num_rays + 1):
        sin_a, cos_a = trigo(curr_angle, trigo_cache)

        x, dx = (xm_block_size, 1) if cos_a >= 0 else (xm, -1)
        for i in range(0, width_height[0], base_block_size):
            depth_v = (x - xo) / cos_a
            yv = yo + depth_v * sin_a
            texture_v = world_map.get(mapping(x + dx, yv), default=None)
            if texture_v is not None:
                break
            x += dx * base_block_size
        depth = depth_v
        offset = yv
        texture = texture_v
        y, dy = (ym_block_size, 1) if sin_a >= 0 else (ym, -1)
        for i in range(0, width_height[1], base_block_size):
            depth_h = (y - yo) / sin_a
            if depth_h >= depth_v:
                break
            xh = xo + depth_h * cos_a
            texture_h = world_map.get(mapping(xh, y + dy), default=None)
            if texture_h is not None:
                depth = depth_h
                offset = xh
                texture = texture_h
                break

            y += dy * base_block_size
        offset = int(offset) % base_block_size
        depth *= math.cos(player_angle - curr_angle)
        proj_height = proj_c / depth
        if proj_height > width_height[1]:
            cf = proj_height / width_height[1]
            new_texture_height = texture_height / cf
            list_of_rays.append(
                (texture, (offset * texture_scale, half_texture_height - new_texture_height // 2, texture_scale,
                           new_texture_height), (scale, width_height[1]),
                 (ray * scale, 0)))

        else:
            list_of_rays.append(
                (texture, (offset * texture_scale, 0, texture_scale, texture_height), (scale, proj_height),
                 (ray * scale, int(half_height - proj_height / 2))))
        curr_angle += delta_angle
    return list_of_rays
