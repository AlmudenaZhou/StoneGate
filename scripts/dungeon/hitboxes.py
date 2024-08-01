from abc import ABC, abstractmethod
from typing import Union, Tuple, Optional

from pygame import Rect

from scripts.geometric_forms import Circle
from scripts.variables import DUN_WIN_X, DUN_WIN_Y


class Hitbox(ABC):

    hitbox: Union[Circle, Rect]
    center_x: float
    center_y: float

    def __init__(self, pos_x, pos_y, width, height):
        """
        It considers that the hitbox is referred to a entity that has a rectangle image.
        :param pos_x: hitbox left x of the entity img hitbox
        :param pos_y: hitbox top y of the entity img hitbox
        :param width: hitbox width of the entity img hitbox
        :param height: hitbox height of the entity img hitbox
        """
        self.center_x = pos_x + width / 2
        self.center_y = pos_y + height / 2

    @abstractmethod
    def create_hitbox(self, pos_x: float, pos_y: float, *args, **kwargs) -> Union[Circle, Rect]:
        pass

    def move(self, hitbox_center, hitbox_measures):
        self.center_x = hitbox_center[0]
        self.center_y = hitbox_center[1]
        self.move_hitbox(hitbox_center, hitbox_measures)

    @abstractmethod
    def move_hitbox(self, hitbox_center: Tuple[float, float], hitbox_measures: Optional[list]):
        pass


class RectangleHitbox(Hitbox):

    def __init__(self, pos_x, pos_y, width, height, ratio=1):
        super(RectangleHitbox, self).__init__(pos_x, pos_y, width, height)
        self.ratio = ratio
        self.hitbox = self.create_hitbox(pos_x, pos_y, width, height)

    def create_hitbox(self, pos_x: float, pos_y: float, width: float, height: float) -> Rect:
        center_x = pos_x + width / 2
        center_y = pos_y + height / 2
        new_pos_x = center_x - width / 2 * self.ratio
        new_pos_y = center_y - height / 2 * self.ratio
        return Rect((new_pos_x, new_pos_y, width * self.ratio, height * self.ratio))

    def move_hitbox(self, hitbox_center: Tuple[float, float], hitbox_measures):
        left = hitbox_center[0] - hitbox_measures[0] * self.ratio / 2
        top = hitbox_center[1] - hitbox_measures[1] * self.ratio / 2
        self.hitbox.update(left, top, hitbox_measures[0] * self.ratio, hitbox_measures[1] * self.ratio)


class CircleHitbox(Hitbox):
    def __init__(self, pos_x, pos_y, width, height, radius):
        super(CircleHitbox, self).__init__(pos_x, pos_y, width, height)
        self.hitbox = self.create_hitbox(self.center_x, self.center_y, radius)

    def create_hitbox(self, center_x: float, center_y: float, radius: float) -> Circle:
        return Circle(center_x, center_y, radius)

    def move_hitbox(self, hitbox_center: Tuple[float, float], hitbox_measures):
        self.hitbox = Circle(hitbox_center[0], hitbox_center[1], self.hitbox.radius)


class NoHitbox(CircleHitbox):

    def __init__(self, pos_x, pos_y, width, height):
        super().__init__(pos_x, pos_y, width, height, 0)


class AllScreenHitbox(RectangleHitbox):
    def __init__(self):
        super().__init__(0, 0, DUN_WIN_X, DUN_WIN_Y)

    def move_hitbox(self, hitbox_center, hitbox_measures):
        pass
