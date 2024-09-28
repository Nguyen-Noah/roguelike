import pygame, math

class Camera:
    def __init__(self, game, size):
        self.game = game
        self.size = size
        self.camera_offset = [0, 0]
        self.int_pos = (0, 0)
        self.target_pos = [0, 0]
        self.rate = 0.25
        self.track_entity = None
        self.restriction_point = None
        self.mode = None
        self.screen_shake = 0
        self.shake_amount = 'medium'

    @property
    def rect(self):
        return pygame.Rect(*self.int_pos, *self.size)

    def focus(self):
        self.update()
        self.true_pos = self.target_pos.copy()

    def move(self, movement):
        self.camera_offset[0] += movement[0]
        self.camera_offset[1] += movement[1]

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
        if target:
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
    
    def __getitem__(self, item):
        return self.int_pos[item]