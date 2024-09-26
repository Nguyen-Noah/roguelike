from .types.shortsword import Shortsword

class WoodSword(Shortsword):
    def attack(self):
        super().attack()
        self.game.world.vfx.spawn_vfx('arc', self.owner.center, (36, 18), 13, 30, -self.angle, distance=50)

    def update(self, dt):
        super().update(dt)

        if not self.attacking:
            self.enable_update = False