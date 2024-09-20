import pygame
from .config import config
from .mgl.mgl import MGL

class Window:
    def __init__(self, game):
        self.game = game

        pygame.init()

        # screen resolution
        self.scaled_resolution = config['window']['scaled_resolution']
        self.base_resolution = config['window']['base_resolution']
        self.scale_ratio = self.scaled_resolution[0] // self.base_resolution[0]

        # opengl
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG, True)

        # clock and fps
        self.fps = config['window']['fps']
        self.clock = pygame.time.Clock()
        self.dt = 1 / self.fps

        # blitting surfs
        self.screen = pygame.display.set_mode(self.scaled_resolution, pygame.OPENGL | pygame.DOUBLEBUF)
        self.display = pygame.Surface(self.base_resolution)
        self.subpixel_surf = pygame.Surface(self.scaled_resolution)
        self.mgl = MGL()

    def render_frame(self):

        self.mgl.render(self.display)
        self.clock.tick(self.fps)
        self.display.fill((0, 0, 0))