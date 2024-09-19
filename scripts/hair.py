from .primitives import vec2

def lerp(v1, v2, t):
    return vec2(v1.x + t * (v2.x - v1.x), v1.y + t * (v2.y - v1.y))


"""
REFERENCE VIDEO: https://www.youtube.com/watch?v=imkT4kFP43k
"""

class HairPart:
    def __init__(self, game, target, img, main_hair_part=False):
        self.game = game
        self.target = target                  # the target position that each hair part wants to be at
        self.img = img
        self.main_hair_part = main_hair_part

        # eventually want to pass in as kwargs
        self.lerp_speed = 5                      # speed in which hair part moves to new distance
        self.max_distance = 3                    # the max distance in which the hair part can move
        self.gravity = 0.5                       # the gravity of the hair part

        self._player_movement = None
        self._ready = False

        self.position = vec2(0, 0)

    def init_hair(self, owner):
        self._player_movement = owner

        # binding the player's hair gravity delegate to the set_gravity() function
        self._player_movement.hair_gravity = self.set_gravity
        self._ready = True

    def on_destroy(self):
        self._player_movement -= self.set_gravity

    def set_gravity(self, new_gravity):
        self.gravity = new_gravity

    def update(self, dt):
        if not self._ready:
            return
        
        # applying gravity
        self.position = vec2(self.position.x, self.position.y + self.gravity)

        difference = vec2(self.position - self.target.position)
        direction = vec2(difference.normalize())
        dist = min(self.max_distance, difference.magnitude())

        # FIX THIS IN VEC2 CLASS TO SUPPORT TUPLE-FLOAT OPERATIONS
        final_pos = vec2(self.target.position.x + direction.x * dist, self.target.position.y + direction.y * dist)

        new_position_lerped = vec2(lerp(final_pos, self.target.position, dt * self.lerp_speed))

        self.position = new_position_lerped

    def render(self, surf):
        #surf.blit(self.img, self.position.tuple)
        self.game.renderer.blit(self.img, self.position.tuple)

class Hair:
    """
    This class is the manager for the hair entity.
    """
    def __init__(self, game, owner):
        """
        :game: used to access assets
        :owner: most likely a Player object, used as anchor for hair
        """
        self.game = game
        self.owner = owner
        self.hair_segments = []

        self.gen_hair()

    def gen_hair(self):
        # Initializing the anchor of the hair, this piece will remain static on the player's head
        self.hair_segments.append(HairPart(self.game, self.owner, self.game.assets.hair['0'], main_hair_part=True))

        for i in range(1, len(self.game.assets.hair)):
            self.hair_segments.append(HairPart(self.game, self.hair_segments[i-1], self.game.assets.hair[str(i)]))

        for segment in self.hair_segments:
            segment.init_hair(self.owner)

    def update(self, dt):
        for segment in self.hair_segments:
            segment.update(dt)
            segment.render()

    def debug(self):
        print('--------------------')
        for i, segment in enumerate(self.hair_segments):
            print(f'Segment {i} at position: {segment.position}')

""" example usage:
    class Player:
        def __init__(self, game, var1, var2):
            self.game = game
            self.var1 = var1
            self.var2 = var2

            self.hair_gravity = None        <- delegate function to change the gravity of each segment
            self.hair = Hair(game, self)    <- game is only needed to access the assets used for each hair segment, can be changed to asset folder for simplification

        def update(self, dt):
            update player

            if self.is_grounded:
                self.hair_gravity(-.1)
            else:
                self.hair_gravity(-.025)
            self.hair.update(dt)

        def render(surf):
            self.hair.render(surf) """

hair_offsets = {
    "path": "idle",
    "hair": [
        (0, -2),
        (0, -2),
        (0, -2),
        (0, -2),
        (0, -1),
        (0, -1),
        (0, -1),
        (0, -1),
        (0, -1)
    ]
}