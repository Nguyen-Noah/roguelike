from .utils import lerp, normalize, magnitude

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

        self.pos = [0, 0]

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
        self.pos[1] = self.pos[1] + self.gravity

        difference = (self.pos[0] - self.target.pos[0], self.pos[1] - self.target.pos[1])
        direction = normalize(difference)
        dist = min(self.max_distance, magnitude(difference))

        final_pos = (self.target.pos[0] + direction[0] * dist, self.target.pos[1] + direction[1] * dist)

        new_pos_lerped = lerp(final_pos, self.target.pos, dt * self.lerp_speed)

        self.pos = new_pos_lerped

        self.render()

    def render(self):
        self.game.renderer.blit(self.img, self.pos)

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

    def debug(self):
        print('--------------------')
        for i, segment in enumerate(self.hair_segments):
            print(f'Segment {i} at pos: {segment.pos}')

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