class GaussianBlur:
    def __init__(self, mgl):
        self.blur = mgl.create_render_object('blur', 'vsBlur')
        self.fbo = mgl.create_fbo()

    def render(self, surf, dest=None):
        self.blur.render(dest=self.fbo, uniforms={
            'surface': surf,
            'horizontal': True
        })
        self.blur.render(dest=dest, uniforms={
            'surface': surf,
            'horizontal': False
        })