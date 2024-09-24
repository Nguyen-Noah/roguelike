import math, random
from .types.shortsword import Shortsword

class WoodSword(Shortsword):
    def update(self, dt):
        super().update(dt)

        if not self.attacking:
            self.enable_update = False