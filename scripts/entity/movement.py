from abc import ABC, abstractmethod

from scripts.dungeon.hitboxes import Hitbox, RectangleHitbox, CircleHitbox
from scripts.utils import collision_between_two_objects
from scripts.variables import DUN_BORDER_X, DUN_WIN_X, DUN_BORDER_Y, DUN_WIN_Y


class Movement(ABC):

    def __init__(self, entity):
        self.entity = entity

    def move(self, all_entities):
        from scripts.entity.entity import Entity
        self._move_entity(all_entities=all_entities)
        self.general_mov_axis()
        self.move_hitboxes()
        if isinstance(self.entity, Entity):
            self.all_movement_checks(all_entities)

    @abstractmethod
    def _move_entity(self, **kwargs):
        pass

    def move_hitboxes(self):
        hitbox_center = (self.entity.pos_x + self.entity.width / 2, self.entity.pos_y + self.entity.height / 2)

        for attribute_name, attribute_value in self.entity.__dict__.items():
            if 'hitbox' in attribute_name:
                assert_hitbox = 'if the attribute name contains hitbox, it must be None or a Hitbox object'
                assert isinstance(attribute_value, Hitbox) or attribute_value is None, assert_hitbox
                if attribute_value is not None and isinstance(attribute_value, RectangleHitbox):
                    attribute_value.move(hitbox_center, [self.entity.width, self.entity.height])
                elif attribute_value is not None and isinstance(attribute_value, CircleHitbox):
                    attribute_value.move(hitbox_center, None)

    def check_entity_collisions(self, all_entities):
        rest_of_entities = [entity for entity in all_entities if entity is not self.entity]
        for entity in rest_of_entities:
            if collision_between_two_objects(entity.draw_hitbox.hitbox, self.entity.draw_hitbox.hitbox):
                self.correct_position_when_collision(entity)

    def correct_position_when_collision(self, entity):
        pass
        # self_center_x = self.entity.draw_hitbox.hitbox.x + self.entity.draw_hitbox.hitbox.width / 2
        # self_center_y = self.entity.draw_hitbox.hitbox.y + self.entity.draw_hitbox.hitbox.height / 2
        # entity_center_x = entity.pos_x + entity.width / 2
        # entity_center_y = entity.pos_y + entity.height / 2

        # mov_direction = [self_center_x - entity_center_x, self_center_y - entity_center_y]
        # overlapped_x = (self.entity.draw_hitbox.hitbox.width / 2 + entity.draw_hitbox.hitbox.width / 2
        #                 - abs(mov_direction[0]))
        # x_mov_direction_sign = mov_direction[0] / abs(mov_direction[0]) if mov_direction[0] != 0 else 0
        # self.entity.pos_x += x_mov_direction_sign * (overlapped_x + 1)
        # overlapped_y = (self.entity.draw_hitbox.hitbox.height / 2 + entity.draw_hitbox.hitbox.height / 2
        #                 - abs(mov_direction[1]))
        # y_mov_direction_sign = mov_direction[1] / abs(mov_direction[1]) if mov_direction[1] != 0 else 0
        # self.entity.pos_y += y_mov_direction_sign * (overlapped_y + 1)

    def check_border_limits(self):
        self.entity.pos_x = min(max(DUN_BORDER_X - (self.entity.width - self.entity.draw_hitbox.hitbox.width),
                                    self.entity.pos_x), DUN_WIN_X - DUN_BORDER_X - self.entity.draw_hitbox.hitbox.width)
        self.entity.pos_y = min(max(DUN_BORDER_Y - (self.entity.height - self.entity.draw_hitbox.hitbox.height),
                                    self.entity.pos_y),
                                DUN_WIN_Y - DUN_BORDER_Y - self.entity.draw_hitbox.hitbox.height)

    def all_movement_checks(self, all_entities):
        self.check_entity_collisions(all_entities)
        self.check_border_limits()

    def general_mov_axis(self):
        self.entity.last_mov_axis = self.entity.mov_axis.copy()
        if self.entity.axis != [0, 0]:
            if self.entity.axis[0] == 0:
                self.entity.mov_axis = self.entity.axis.copy()
            else:
                self.entity.mov_axis = [self.entity.axis[0], 0]

        # Fix the position of the pj from the pj hitbox instead of the img hitbox
        if self.entity.last_mov_axis == [-1, 0] and self.entity.last_mov_axis != self.entity.mov_axis:
            self.entity.pos_x = self.entity.draw_hitbox.hitbox.x
        elif self.entity.last_mov_axis == [1, 0] and self.entity.mov_axis == [-1, 0]:
            self.entity.pos_x = (self.entity.draw_hitbox.hitbox.x + self.entity.draw_hitbox.hitbox.width
                                 - self.entity.width)


class BaseMovement(Movement):

    def _move_entity(self, **kwargs):
        if self.entity.axis[0] != 0 and self.entity.axis[1] != 0:
            vel_mod = (self.entity.axis[0] ** 2 + self.entity.axis[1] ** 2) ** (1 / 2)
        else:
            vel_mod = 1

        self.entity.pos_x += self.entity.vel * self.entity.axis[0] / vel_mod
        self.entity.pos_y += self.entity.vel * self.entity.axis[1] / vel_mod


class NoMovement(Movement):

    def _move_entity(self, **kwargs):
        pass


class MovementDecorator(Movement):

    _movement_behaviour: Movement = None

    def __init__(self, entity, movement_behaviour):
        super(MovementDecorator, self).__init__(entity)
        self._movement_behaviour = movement_behaviour(entity)

    @property
    def movement_behaviour(self) -> Movement:
        return self._movement_behaviour

    def _move_entity(self, **kwargs):
        self._movement_behaviour._move_entity()


class MovementTowardsSomething(MovementDecorator):

    def __init__(self, entity):
        super(MovementTowardsSomething, self).__init__(entity, BaseMovement)

    def _move_entity(self, all_entities):
        object_to_follow = all_entities[0]  # TODO: modify the way this is called
        x_axis = int(object_to_follow.pos_x + object_to_follow.width / 2
                     - (self.entity.pos_x + self.entity.width / 2))
        y_axis = int(object_to_follow.pos_y + object_to_follow.height / 2
                     - (self.entity.pos_y + self.entity.height / 2))

        if abs(x_axis) > (self.entity.width / 2):
            if x_axis > 0:
                self.entity.axis[0] = 1
            elif x_axis < 0:
                self.entity.axis[0] = -1
        else:
            self.entity.axis[0] = 0

        if abs(y_axis) > (self.entity.height / 2):
            if y_axis > 0:
                self.entity.axis[1] = 1
            elif y_axis < 0:
                self.entity.axis[1] = -1
        else:
            self.entity.axis[1] = 0
        super(MovementTowardsSomething, self)._move_entity()
