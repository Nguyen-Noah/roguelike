class Block:
    def __init__(self, mgl):
        self.base = mgl.create_render_object('default', 'vsDefault')

    def update(self, uniforms={}):
        self.base.update(uniforms=uniforms)

    def render(self, uniforms, dest=None):
        self.base.render(dest=dest, uniforms={
            'surface': uniforms['surface'],
            'projection': uniforms['projection']
        })