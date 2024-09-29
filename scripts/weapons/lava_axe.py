from .types.greataxe import Greataxe

class LavaAxe(Greataxe):
    def update(self, dt):
        super().update(dt)

        if not self.attacking:
            self.enable_update = False