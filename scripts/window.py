import pygame, time
from .config import config
from .mgl.mgl import MGL

class Window:
    def __init__(self, game):
        self.game = game

        pygame.init()

        # screen resolution
        self.resolution = config['window']['resolution']
        self.scale_ratio = config['window']['scale_ratio']
        self.offset = (0, 0)

        # opengl
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)

        # clock and fps
        self.fps_cap = config['window']['fps']
        self.dt_cap = 1
        self.time = time.time()
        self.start_time = time.time()
        self.frames = 0
        self.frame_log = []
        self.clock = pygame.time.Clock()
        self.last_frame = time.time()
        self.dt = 0.1

        # blitting surfs
        self.screen = pygame.display.set_mode(self.resolution, pygame.OPENGL | pygame.DOUBLEBUF)
        self.display = pygame.Surface(self.resolution)
        self.mgl = MGL()

    @property
    def fps(self):
        return len(self.frame_log) / sum(self.frame_log)

    def render_frame(self):
        self.dt = min(time.time() - self.last_frame, self.dt_cap)
        self.frame_log.append(self.dt)
        self.frame_log = self.frame_log[-60:]
        self.last_frame = time.time()

        self.mgl.render(self.display, self.time, self.game.input.mouse.pos)
        self.clock.tick(self.fps_cap)
        self.display.fill((0, 0, 0))
        self.time = time.time()
        self.frames += 1
        print(f'fps: {self.fps}')