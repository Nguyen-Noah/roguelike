import moderngl, pygame
from array import array

class RenderObject:
    def __init__(self, mgl_manager, frag_shader, vert_shader=None, default_ro=False, vao_args=['2f 2f', 'vert', 'texcoord'], buffer=None):
        self.mgl = mgl_manager
        if not vert_shader:
            vert_shader = self.mgl.default_vert
        self.default = default_ro
        self.raw_frag = frag_shader
        self.raw_vert = vert_shader
        self.vao_args = vao_args
        self.program = self.mgl.ctx.program(vertex_shader=vert_shader, fragment_shader=frag_shader)
        if not buffer:
            buffer = self.mgl.quad_buffer
        self.vao = self.mgl.ctx.vertex_array(self.program, [(buffer, *vao_args)])
        self.temp_textures = []
        self.debug = False

    def update(self, uniforms={}):
        tex_id = 0
        uniform_list = list(self.program)
        for uniform in uniforms:
            if uniform in uniform_list:
                if type(uniforms[uniform]) == moderngl.Texture:
                    # bind tex to next ID
                    uniforms[uniform].use(tex_id)
                    # specify tex ID as uniform target
                    self.program[uniform].value = tex_id
                    tex_id += 1
                else:
                    if uniform == 'projection':
                        self.program[uniform].write(uniforms[uniform].astype('f4').tobytes())
                    else:
                        self.program[uniform].value = uniforms[uniform]
                    
    def parse_uniforms(self, uniforms):
        for name, value in uniforms.items():
            if type(value) == pygame.Surface:
                tex = self.mgl.pg2tx(value)
                uniforms[name] = tex
                self.temp_textures.append(tex)
        return uniforms
        
    def render(self, dest=None, uniforms={}):
        if not dest:
            dest = self.mgl.ctx.screen
            
        dest.use()
        uniforms = self.parse_uniforms(uniforms)
        self.update(uniforms=uniforms)
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)
        
        for tex in self.temp_textures:
            tex.release()
        self.temp_textures = []

class Renderer:
    def __init__(self, mgl, program):
        self.mgl = mgl
        self.program = program
        self.vao = None
        self.vbo = None

    def create_vao(self, args=['2f 2f', 'vert', 'texcoord']):
        if self.vao:
            self.vao.release()
        self.vao = self.mgl.ctx.vertex_array(self.program, [(self.vbo, *args)])

    def create_vbo(self, rect, resolution, ctx, angle=0, raw=False):
        win_w, win_h = resolution
        l, t, r, b = rect
        r_w_w = 1 / win_w
        r_w_h = 1 / win_h
        no_t = (t * r_w_h) * -2 + 1
        no_b = ((t + b) * r_w_h) * -2 + 1
        no_l = (l * r_w_w) * 2 - 1
        no_r = ((r + l) * r_w_w) * 2 - 1 

        buffer = [
                # position (x, y), uv coords (x, y)
                no_l, no_t, 0, 0,  # topleft
                no_r, no_t, 1, 0,  # topright
                no_l, no_b, 0, 1,  # bottomleft
                no_r, no_b, 1, 1,  # bottomright
            ]

        self.vbo = self.mgl.ctx.buffer(data=array('f', buffer)) if not raw else buffer
        self.create_vao()

    def update(self, uniforms={}):
        tex_id = 0
        uniform_list = list(self.program)
        for uniform in uniforms:
            if uniform in uniform_list:
                if type(uniforms[uniform]) == moderngl.Texture:
                    # bind tex to next ID
                    uniforms[uniform].use(tex_id)
                    # specify tex ID as uniform target
                    self.program[uniform].value = tex_id
                    tex_id += 1
                else:
                    self.program[uniform].value = uniforms[uniform]

    def render(self, dest=None, uniforms={}):
        if not dest:
            dest = self.mgl.ctx.screen

        dest.use()
        self.update(uniforms=uniforms)
        self.vao.render(mode=moderngl.TRIANGLE_STRIP)