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

class Quads:
    def __init__(self, quad_size):
        self.quad_size = quad_size
        self.reset()

    def reset(self):
        self.objects = {}
        self.map = {}
        self.id_to_loc = {}
        self.next_id = 0
        
    def export(self, obj_handler=lambda x: None):
        output = {
            'objects': {k: obj_handler(v) for k, v in self.objects.items()},
            'map': self.map,
            'id_to_loc': self.id_to_loc,
            'next_id': self.next_id,
        }
        return output

    def add(self, obj, quad_loc, tag=False, id_jump=1):
        if tag:
            obj.quad_ids.append(self.next_id)
        self.objects[self.next_id] = obj
        if self.next_id not in self.id_to_loc:
            self.id_to_loc[self.next_id] = []
        self.id_to_loc[self.next_id].append(quad_loc)
        if quad_loc not in self.map:
            self.map[quad_loc] = []
        self.map[quad_loc].append(self.next_id)
        self.next_id += id_jump

    def add_raw(self, obj, rect, tag=False):
        if tag:
            obj.quad_ids = []
        quad_locs = [
            (rect.x // self.quad_size, rect.y // self.quad_size),
            (rect.x + rect.width // self.quad_size, rect.y // self.quad_size),
            ((rect.x + rect.width) // self.quad_size, (rect.y + rect.height) // self.quad_size),
            (rect.x // self.quad_size, (rect.y + rect.height) // self.quad_size),
        ]
        quad_locs = set(quad_locs)
        for loc in quad_locs:
            self.add(obj, loc, tag=tag, id_jump=0)
        self.next_id += 1
    
    def delete(self, obj):
        # assumes object is tagged
        for quad_id in obj.quad_ids:
            if quad_id in self.objects:
                del self.objects[quad_id]
            try:
                for loc in self.id_to_loc[quad_id]:
                     if loc in self.map:
                        if quad_id in self.map[loc]:
                            self.map[loc].remove(quad_id)
            except KeyError:
                continue
            del self.id_to_loc[quad_id]

    def query(self, rect):
        # get bounding coords
        tl = (rect.x // self.quad_size, rect.y // self.quad_size)
        br = ((rect.x + rect.width) // self.quad_size, (rect.y + rect.height) // self.quad_size)

        # lookup entries
        results = []
        for x in range(br[0] - tl[0] + 2):
            for y in range(br[1] - tl[1] + 2):
                loc = (tl[0] + x - 1, tl[1] + y - 1)
                if loc in self.map:
                    results += self.map[loc]

        # remove duplicates
        results = set(results)

        return [self.objects[obj_id] for obj_id in results]