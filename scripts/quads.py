class EQuads:
    def __init__(self, quad_size=64):
        self.quad_size = quad_size
        self.reset()

    def reset(self):
        self.quads = {}
        self.known_locs = {}
        self.active_entities = {}

    @property
    def count(self):
        return sum([len(self.quads[quad]) for quad in self.quads])
    
    def insert(self, entity, egroup='default'):
        if id(entity) not in self.known_locs:
            quad = (int(entity.pos[0] // self.quad_size), int(entity.pos[1] // self.quad_size))
            if quad not in self.quads:
                self.quads[quad] = quad
            self.quads[quad].append(entity)
            self.known_locs[id(entity)] = quad

            entity._egroup = egroup
            if egroup not in self.active_entities:
                self.active_entities[egroup] = []

    def delete(self, entity):
        if id(entity) in self.known_locs:
            self.quads[self.known_locs[id(entity)]].remove(entity)
            del self.known_locs[id(entity)]

    def update(self, rect):
        for group in self.active_entities:
            self.active_entities[group] = []

        for y in range(int(rect.top // self.quad_size), int(rect.bottom // self.quad_size + 1)):
            for x in range(int(rect.left // self.quad_size), int(rect.right // self.quad_size + 1)):
                loc = (x, y)
                if loc in self.quads:
                    for entity in self.quads[loc]:
                        new_quad = (int(entity.pos[0] // self.quad_size), int(entity.pos[1] // self.quad_size))
                        
                        # move entityect's quad if necessary
                        if self.known_locs[id(entity)] != new_quad:
                            old_quad = self.known_locs[id(entity)]
                            self.known_locs[id(entity)] = new_quad
                            self.quads[old_quad].remove(entity)
                            if new_quad not in self.quads:
                                self.quads[new_quad] = []
                            self.quads[new_quad].append(entity)
                        
                        # mark object as active
                        self.active_entities[entity._egroup].append(entity)