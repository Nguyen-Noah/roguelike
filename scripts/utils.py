import math, json, pygame, os

def lerp(v1, v2, t):
    return [v1[0] + t * (v2[0] - v1[0]), v1[1] + t * (v2[1] - v1[1])]

def advance(pos, angle, amt):
    pos[0] += math.cos(angle) * amt
    pos[1] += math.sin(angle) * amt
    return pos

def magnitude(vec):
    return math.sqrt(vec[0] ** 2 + vec[1] ** 2)

def normalize(vec):
    mag = magnitude(vec)
    if mag > 0:
        return (vec[0] / mag, vec[1] / mag)
    return (0, 0)

def read_json(path):
    f = open(path, 'r')
    data = json.load(f)
    f.close()
    return data

def write_json(path, data):
    f = open(path, 'w')
    json.dump(data, f)
    f.close()

def load_img(path, alpha=False, colorkey=None):
    if alpha:
        img = pygame.image.load(path).convert_alpha()
    else:
        img = pygame.image.load(path).convert()
    if colorkey:
        img.set_colorkey(colorkey)
    return img


# assets
def recursive_file_op(path, func, game=None, filetype=None):
    data = {}
    base_path = path.split('/')
    for f in os.walk(path):
        wpath = f[0].replace('\\', '/').split('/')
        path_ref = wpath.copy()
        data_ref = data

        # iteratively generate file structure
        while len(path_ref) > len(base_path):
            current_dir = path_ref[len(base_path)]
            if current_dir not in data_ref:
                data_ref[current_dir] = {}
            data_ref = data_ref[current_dir]
            path_ref.pop(len(base_path))

        # load assets
        for asset in f[2]:
            asset_type = asset.split('.')[-1]
            if (asset_type == filetype) or (filetype == None):
                if game:
                    data_ref[asset.split('.')[0]] = func(game, f[0] + '/' + asset)
                else:
                    data_ref[asset.split('.')[0]] = func(f[0] + '/' + asset)

    return data

def load_img_directory(path, alpha=False, colorkey=None):
    return recursive_file_op(path, lambda x: load_img(x, alpha=alpha, colorkey=colorkey), filetype='png')

def clip(surf, rect):
    if type(rect) == tuple:
        rect = pygame.Rect(*rect)
    surf.set_clip(rect)
    image = surf.subsurface(surf.get_clip()).copy()
    surf.set_clip(None)
    return image

def palette_swap(surf, colors):
    colorkey = surf.get_colorkey()
    surf = surf.copy()
    for from_color, to_color in colors.items():
        surf.set_colorkey(from_color)
        if len(to_color) <= 3: 
            dest = pygame.Surface(surf.get_size())
        else:
            dest = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        dest.fill(to_color)
        dest.blit(surf, (0, 0))
        surf = dest
    surf.set_colorkey(colorkey)
    return surf

def collision_list(obj, obj_list):
    hit_list = []
    for r in obj_list:
        if obj.colliderect(r):
            hit_list.append(r)
    return hit_list

def smooth_approach(val, target, dt, slowness=1):
    val += (target - val) / slowness * min(dt, slowness)
    return val

def ease_out_cubic(t):
    t -= 1
    return t * t * t + 1



# I/O
def tuplestrkey(obj):
    if type(obj) == tuple:
        obj = 't\0' + str(obj).replace(' ', '')
    return obj

def tuple_change_keys(obj, convert):
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for k, v in obj.items():
            new[convert(k)] = tuple_change_keys(v, convert)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(tuple_change_keys(v, convert) for v in obj)
    else:
        return obj
    return new

def tjson_encode(data):
    return json.dumps(tuple_change_keys(data, tuplestrkey))

def write_f(path, data):
    f = open(path, 'w')
    f.write(data)
    f.close()

def read_f(path):
    f = open(path, 'r')
    data = f.read()
    f.close()
    return data
    
def tjson_hook(obj):
    if type(obj) == dict:
        for key in list(obj):
            if (type(key) == str) and (key.translate({ord(k): None for k in ' (),t\0'}).isalnum()) and (key.find(',') != -1) and (key[:2] == 't\0'):
                new_key = tuple(int(v) for v in key.translate({ord(k): None for k in ' ()t\0'}).split(','))
                obj[new_key] = obj[key]
                del obj[key]
    return obj

def tjson_hook_loose(obj):
    if type(obj) == dict:
        for key in list(obj):
            if (type(key) == str) and (key.translate({ord(k): None for k in ' (),t\0'}).isalnum()) and (key.find(',') != -1):
                new_key = tuple(int(v) for v in key.translate({ord(k): None for k in ' ()t\0'}).split(','))
                obj[new_key] = obj[key]
                del obj[key]
    return obj

def read_json(path):
    f = open(path, 'r')
    data = json.load(f)
    f.close()
    return data

def tjson_decode(data, loose=False):
    if loose:
        return json.loads(data, object_hook=tjson_hook_loose)
    else:
        return json.loads(data, object_hook=tjson_hook)

def read_tjson(path, loose=False):
    return tjson_decode(read_f(path), loose=loose)

def write_tjson(path, data):
    write_f(path, tjson_encode(data))

def rectify(p1, p2):
    tl = (min(p1[0], p2[0]), min(p1[1], p2[1]))
    br = (max(p1[0], p2[0]), max(p1[1], p2[1]))
    return pygame.Rect(*tl, br[0] - tl[0] + 1, br[1] - tl[1] + 1)
