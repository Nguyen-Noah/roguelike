import moderngl, pygame

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