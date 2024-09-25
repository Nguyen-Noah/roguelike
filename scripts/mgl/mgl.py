import moderngl, pygame
import numpy as np
from array import array
from .render_object import RenderObject


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
    def __init__(self):
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

    def initialize(self):
        # CREATE ALL SHADER PROGRAMS/FRAMEBUFFERS ---------- #
        self.default_shader = RenderObject(self, self.default_frag, self.default_vert, vao_args=['2f 2f', 'vert', 'texcoord'], buffer=None)
        #self.test_shader = self.create_render_object('test', 'vert')

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
        self.default_shader.render(uniforms={
            'surface': surface
        })

        self.ctx.disable(moderngl.BLEND)
        pygame.display.flip()