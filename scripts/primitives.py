import math

class vec2:
    def __init__(self, *args):
        """
        Initionalize the vector2
        :position: two-length tuple (x, y)
        :angle: angle, in degrees counterclockwise from right
        """
        if len(args) == 1 and isinstance(args[0], vec2):
            self._x, self._y = args[0].position
        elif len(args) == 1 and isinstance(args[0], tuple):
            self._x, self._y = args[0][0], args[0][1]
        elif len(args) == 2:
            self.x, self.y = args
        else:
            raise ValueError('Invalid number of arguments. Expected either a tuple or two integers.')

    def normalize(self):
        mag = self.magnitude()
        if mag > 0:
            return vec2(self.x / mag, self.y / mag)
        return vec2(0, 0)

    def magnitude(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)
    
    def copy(self):
        return vec2(self.x, self.y)
    
    @property
    def tuple(self):
        return (self.x, self.y)

    @property
    def position(self):
        return (self.x, self.y)

    @position.setter
    def position(self, new_position):
        self.x = new_position[0]
        self.y = new_position[1]

    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value

    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value

    
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return vec2(self.x + other, self.y + other)
        elif isinstance(other, vec2):
            return vec2(self.x + other.x, self.y + other.y)
        else:
            raise TypeError("Addition only supports int, float, or vec2")

    def __iadd__(self, other):
        if isinstance(other, (int, float)):
            self.x += other
            self.y += other
        elif isinstance(other, vec2):
            self.x += other.x
            self.y += other.y
        else:
            raise TypeError("Addition only supports int, float, or vec2")
        return self
    
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return vec2(self.x - other, self.y - other)
        elif isinstance(other, vec2):
            return vec2(self.x - other.x, self.y - other.y)
        else:
            raise TypeError("Subtraction only supports int, float, or vec2")

    
    def __isub__(self, other):
        if isinstance(other, (int, float)):
            self.x -= other
            self.y -= other
        elif isinstance(other, vec2):
            self.x -= other.x
            self.y -= other.y
        else:
            raise TypeError("Subtraction only supports int, float, or vec2")
        return self
    
    def __mul__(self, scalar):
        if isinstance(scalar, (int, float)):
            return vec2(self.x * scalar, self.y * scalar)
        else:
            raise TypeError("Multiplication only supports int, float, or vec2")

    def __imul__(self, scalar):
        if isinstance(scalar, (int, float)):
            self.x *= scalar
            self.y *= scalar
        elif isinstance(scalar, vec2):
            self.x *= scalar.x
            self.y *= scalar.y
        else:
            raise TypeError('Scalar multiplication only supports int, float, or vec2')
        return self

    def __truediv__(self, divisor):
        if isinstance(divisor, (int, float)):
            return vec2(self.x * divisor, self.y * divisor)
        else:
            raise TypeError("Division only supports int, float, or vec2")

    def __itruediv__(self, divisor):
        if isinstance(divisor, (int, float)):
            self.x *= divisor
            self.y *= divisor
        elif isinstance(divisor, vec2):
            self.x *= divisor.x
            self.y *= divisor.y
        else:
            raise TypeError('Scalar division only supports int, float, or vec2')
        return self

    def __str__(self):
        return f'({self.x}, {self.y})'
    
    def __repr__(self):
        return self.__str__()