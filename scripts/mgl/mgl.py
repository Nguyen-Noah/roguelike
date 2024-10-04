import moderngl, pygame
import numpy as np
from array import array
from .render_object import RenderObject, Renderer
from .lib import Block

def read_f(path):
    f = open(f'scripts/mgl/shaders/{path}.glsl', 'r')
    data = f.read()
    f.close()
    return data

default_vert_shader = '''
#version 330

in vec2 vert;
in vec2 texcoord;
out vec2 uv;

void main() {
  uv = texcoord;
  gl_Position = vec4(vert, 0.0, 1.0);
}
'''

default_frag_shader = '''
#version 330

uniform sampler2D surface;

out vec4 f_color;
in vec2 uv;

void main() {
  f_color = vec4(texture(surface, uv).rgb, 1.0);
}
'''

class MGL():
    def __init__(self, game):
        self.game = game
        self.ctx = moderngl.create_context(require=330)
        self.quad_buffer = self.ctx.buffer(data=array('f', [
            # position (x, y), uv coords (x, y)
            -1.0, 1.0, 0.0, 0.0,  # topleft
            1.0, 1.0, 1.0, 0.0,   # topright
            -1.0, -1.0, 0.0, 1.0, # bottomleft
            1.0, -1.0, 1.0, 1.0,  # bottomright
        ]))

        self.quad_buffer_notex = self.ctx.buffer(data=array('f', [
            # position (x, y)
            -1.0, 1.0,
            -1.0, -1.0,
            1.0, 1.0,
            1.0, -1.0,
        ]))

        self.default_vert = default_vert_shader
        self.default_frag = default_frag_shader

        self.initialize()

    @property
    def projection_matrix(self):
        c = self.game.camera
        # Define the left, right, top, bottom for the orthographic view
        left = c.camera_offset[0]
        right = left + self.game.window.resolution[0] / c.zoom
        bottom = c.camera_offset[1]
        top = bottom + self.game.window.resolution[1] / c.zoom

        # Orthographic projection matrix
        return np.array([
            [2 / (right - left), 0, 0, -(right + left) / (right - left)],
            [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
            [0, 0, -1, 0],
            [0, 0, 0, 1]
        ], dtype='f4')

    def initialize(self):
        # CREATE ALL SHADER PROGRAMS/FRAMEBUFFERS ---------- #
        tile = self.ctx.program(fragment_shader=read_f('default'), vertex_shader=read_f('vsDefault'))
        self.tile = Renderer(self, tile)

    def default_ro(self):
        return RenderObject(self.default_frag, default_ro=True)
        
    def create_render_object(self, frag_path, vert_shader=None, vao_args=['2f 2f', 'vert', 'texcoord'], buffer=None):
        frag_shader = read_f(frag_path)
        if vert_shader:
            vert_shader = read_f(vert_shader)
        return RenderObject(self, frag_shader, vert_shader=vert_shader, vao_args=vao_args, buffer=buffer)
    
    def tx2pg(self, tex):
        channels = 3
        texture_data = tex.read()
        pg_surf = pygame.Surface((tex.width, tex.height), pygame.SRCALPHA)
        np_array = np.frombuffer(texture_data, dtype=np.uint8).reshape((tex.width, tex.height, channels))
        pygame.surfarray.blit_array(pg_surf, np_array)
        return pg_surf
            
    def pg2tx(self, surf):
        channels = 4
        new_tex = self.ctx.texture(surf.get_size(), channels)
        new_tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        new_tex.swizzle = 'BGRA'
        new_tex.write(surf.get_view('1'))
        return new_tex
    
    def pg2tx_update(self, tex, surf):
        tex.write(surf.get_view('1'))
        return tex
    
    def create_fbo(self):
        channels = 4
        new_fbo = self.ctx.texture((1080, 720), channels)
        new_fbo.filter = (moderngl.NEAREST, moderngl.NEAREST)
        return self.ctx.framebuffer(color_attachments=[new_fbo])
    
    def render(self, surface, time, mouse_pos):
        self.ctx.clear()
        self.ctx.enable(moderngl.BLEND)

        # rendering pipeline --------------- #
        """ self.block_program.update(uniforms={
            'projection': self.projection_matrix
        }) """
        self.game.world.tilemap.render()

        self.ctx.disable(moderngl.BLEND)
        pygame.display.flip()