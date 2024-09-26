""" import random

import pygame

from .utils import smooth_approach

class Camera:
    def __init__(self, game, size, pos=(0, 0), slowness=1, tilemap_lock=None):
        self.game = game
        self.size = size
        self.slowness = slowness
        self.pos = list(pos)
        self.base_pos = self.pos.copy()
        self.int_pos = (int(self.pos[0]), int(self.pos[1]))
        self.target_entity = None
        self.target_pos = None
        self.tilemap_lock = tilemap_lock

        self.rect_exp = pygame.Rect(self.int_pos[0] - 5, self.int_pos[1] - 5, self.size[0] + 10, self.size[1] + 10)

        self.screenshake = 0

    @property
    def rect(self):
        return pygame.Rect(*self.int_pos, *self.size)
    
    @property
    def target(self):
        print(self.game.input.mouse.pos)
        if self.target_entity:
            world_mpos = pygame.Vector2(self.game.input.mouse.pos[0] + self.pos[0], self.game.input.mouse.pos[1] + self.pos[1])
            print(world_mpos)
            return ((world_mpos - pygame.Vector2(self.size) * 0.5)+ (self.target_entity.center[0] - self.size[0] // 2, self.target_entity.center[1] - self.size[1] // 2))
        elif self.target_pos:
            return (self.target_pos[0] - self.size[0] // 2, self.target_pos[0] - self.size[1] // 2)
    
    def set_target(self, target):
        if hasattr(target, 'center'):
            self.target_entity = target
            self.target_pos = None
        elif target:
            self.target_pos = tuple(target)
            self.target_entity = None
        else:
            self.target_pos = None
            self.target_entity = None
            
    def __iter__(self):
        for v in self.int_pos:
            yield v
        
    def __getitem__(self, item):
        return self.int_pos[item]
    
    def move(self, movement):
        self.base_pos[0] += movement[0]
        self.base_pos[1] += movement[1]
    
    def update(self):
        dt = self.game.window.dt

        self.screenshake = max(0, self.screenshake - dt)

        target = self.target
        if target:
            self.base_pos[0] = smooth_approach(self.base_pos[0], target[0], dt, slowness=self.slowness)
            self.base_pos[1] = smooth_approach(self.base_pos[1], target[1], dt, slowness=self.slowness)
            if self.tilemap_lock:
                self.base_pos[0] = max(0, min(self.tilemap_lock.dimensions[0] * self.tilemap_lock.tile_size - self.size[0], self.base_pos[0]))
                self.base_pos[1] = max(0, min(self.tilemap_lock.dimensions[1] * self.tilemap_lock.tile_size - self.size[1], self.base_pos[1]))

        self.pos = self.base_pos.copy()
        if self.screenshake:
            self.pos = [self.base_pos[0] + (random.random() - 0.5) * 4, self.base_pos[1] + (random.random() - 0.5) * 6]

        self.int_pos = (int(self.pos[0]), int(self.pos[1]))

        self.rect_exp = pygame.Rect(self.int_pos[0] - 5, self.int_pos[1] - 5, self.size[0] + 10, self.size[1] + 10) """
    
import math, random
from .config import config

class Camera:
    def __init__(self, game):
        self.game = game
        self.camera_offset = [0, 0]
        self.int_pos = (0, 0)
        self.target_pos = [0, 0]
        self.rate = 0.25
        self.track_entity = None
        self.restriction_point = None
        self.mode = None
        self.screen_shake = 0
        self.shake_amount = 'medium'

    def focus(self):
        self.update()
        self.true_pos = self.target_pos.copy()

    def set_tracked_entity(self, entity):
        self.track_entity = entity

    def set_restriction(self, pos):
        self.restriction_point = list(pos)

    def add_screen_shake(self, duration, amt='medium'):
        self.screen_shake = duration
        self.shake_amount = amt

    @property
    def target(self):
        if self.track_entity:
            if self.track_entity.type == 'player':
                target_pos = self.track_entity.pos.copy()
                if self.track_entity.weapon:
                    angle = math.radians(self.track_entity.weapon.angle)
                    dis = math.sqrt((self.game.input.mouse.pos[1] - self.track_entity.center[1] + self.render_offset[1]) ** 2 + (self.game.input.mouse.pos[0] - self.track_entity.center[0] + self.render_offset[0]) ** 2)
                    target_pos[0] += math.cos(angle) * (dis / 8)
                    target_pos[1] += math.sin(angle) * (dis / 8)
            return (target_pos[0] - self.game.window.display.get_width() // 2, target_pos[1] - self.game.window.display.get_height() // 2)

    def update(self):
        self.int_pos = (int(self.camera_offset[0]), int(self.camera_offset[1]))

        """ if self.screen_shake:
            amt = config['camera'][self.shake_amount]
            self.true_pos[0] += random.randint(0, amt*2) - amt
            self.true_pos[1] += random.randint(0, amt*2) - amt
            self.screen_shake -= 1 """

        # Core Camera Functionality -------------------------- #
        target = self.target
        self.camera_offset[0] += math.floor(target[0] - self.camera_offset[0]) / (self.rate / self.game.window.dt)
        self.camera_offset[1] += math.floor(target[1] - self.camera_offset[1]) / (self.rate / self.game.window.dt)

        if self.restriction_point:
            if self.camera_offset[0] + self.game.window.display.get_width() // 2 - self.restriction_point[0] > self.lock_distance[0]:
                self.camera_offset[0] = self.restriction_point[0] - self.game.window.display.get_width() // 2 + self.lock_distance[0]
            if self.camera_offset[0] + self.game.window.display.get_width() // 2 - self.restriction_point[0] < -self.lock_distance[0]:
                self.camera_offset[0] = self.restriction_point[0] - self.game.window.display.get_width() // 2 - self.lock_distance[0]
            if self.camera_offset[1] + self.game.window.display.get_height() // 2 - self.restriction_point[1] > self.lock_distance[1]:
                self.camera_offset[1] = self.restriction_point[1] - self.game.window.display.get_height() // 2 + self.lock_distance[1]
            if self.camera_offset[1] + self.game.window.display.get_height() // 2 - self.restriction_point[1] < -self.lock_distance[1]:
                self.camera_offset[1] = self.restriction_point[1] - self.game.window.display.get_height() // 2 - self.lock_distance[1]

    @property
    def render_offset(self):
        return [self.camera_offset[0] - self.game.window.offset[0], self.camera_offset[1] - self.game.window.offset[1]]

    @property
    def pos(self):
        return (int(math.floor(self.camera_offset[0])), int(math.floor(self.camera_offset[1])))