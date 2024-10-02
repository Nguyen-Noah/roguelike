class Base:
    def __init__(self, mgl):
        self.base = mgl.create_render_object('default', 'vsDefault')

    def render(self, dest, projection_mat):
        self.base.render(dest=dest, uniforms={
            
        })