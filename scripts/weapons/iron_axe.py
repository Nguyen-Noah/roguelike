from .types.greataxe import Greataxe

class IronAxe(Greataxe):
    def update(self, dt):
        super().update(dt)

        if not self.attacking:
            self.enable_update = False