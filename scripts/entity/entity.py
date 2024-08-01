from abc import ABC, abstractmethod

from scripts.draw import Draw, DrawSuppEntityHitbox, DrawAnimationEntityWithLifeBar
from scripts.entity.attack import Attack, MovAxisDistanceAttack
from scripts.entity.movement import Movement, BaseMovement
from scripts.dungeon.hitboxes import RectangleHitbox


class Entity(ABC):

    inferior_x_limit = None
    superior_x_limit = None
    inferior_y_limit = None
    superior_y_limit = None

    attack: Attack
    movement: Movement
    draw: Draw

    def __init__(self, pos_x, pos_y, width, height, vel, animation_database, damage, hp, **kwargs):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.vel = vel
        self.damage = damage
        self.hp = hp
        self.max_hp = hp

        self.draw = DrawAnimationEntityWithLifeBar(self, animation_database)  # DrawAnimationEntityWithLifeBar. DrawSuppEntityHitbox

        self.first_attack = False

        self.state = 'parada'
        self.attacking = False
        self.moving = False
        self.max_attack_cooldown = len(animation_database['atacar'][(1, 0)])
        self.attack_cooldown = 0
        self.axis = [0, 0]
        self.mov_axis = [1, 0]
        self.action_var = [self.state, self.axis]
        self.last_state = 'parada'
        self.last_axis = [0, 0]
        self.last_mov_axis = [1, 0]

        self.animation_database = animation_database
        self.draw_hitbox = RectangleHitbox(pos_x, pos_y, width, height)

        self.attack_hitbox = RectangleHitbox(pos_x, pos_y, width, height)
        self.defense_hitbox = self.get_defense_entity_hitbox()
        self.vision_hitbox = None

    def set_attack_attributes(self):
        self.attacking = True
        self.attack_cooldown = self.max_attack_cooldown

    def change_action(self, action_var):
        new_value = [self.state, self.axis]
        self.first_attack = False
        if action_var != new_value:
            if 'atacar' in new_value:
                self.first_attack = True
            self.draw.frames = 0
        self.last_state = action_var[0]
        self.last_axis = action_var[1]

    def get_state(self):
        if self.attacking and self.moving:
            self.state = 'caminar_atacar'
        elif self.attacking:
            self.state = 'atacar'
        elif self.moving:
            self.state = 'caminar'
        else:
            self.state = 'parada'

    def set_attributes_before_turn(self):
        pass

    def set_attributes_after_turn(self):
        self.axis = [0, 0]
        self.moving = False
        self.attack_cooldown -= 1
        if self.attack_cooldown < 0:
            self.attacking = False

    def turn(self, all_entities):
        action_var = [self.state, self.axis].copy()
        self.set_attributes_before_turn()

        self.movement.move(all_entities)

        projectile = self.prepare_attack(all_entities)

        self.change_action(action_var)
        self.get_state()
        self.set_attributes_after_turn()
        return projectile

    @abstractmethod
    def prepare_attack(self, all_entities):
        pass

    def get_defense_entity_hitbox(self):
        return RectangleHitbox(self.pos_x, self.pos_y, self.width, self.height)

    @abstractmethod
    def initialize_projectile(self, proj_width, proj_height):
        pass


class Pj(Entity):

    def __init__(self, pos_x, pos_y, width, height, vel, animation_database, damage, hp, sword, **kwargs):
        super(Pj, self).__init__(pos_x, pos_y, width, height, vel, animation_database, damage, hp)
        self.sword = sword
        self.element = self.sword.element
        self.attack: Attack = MovAxisDistanceAttack()
        self.movement: Movement = BaseMovement(self)

        self.door_hitbox = RectangleHitbox(pos_x, pos_y, width, height, 1)

        self.crossing_door_count = 0

    def cross_door(self, door):
        """
        Considers the borders in order to avoid the pj to be stuck
        :param door:
        :return:
        """
        self.pos_x = door.pos_x
        self.pos_y = door.pos_y
        self.movement.check_border_limits()

    def prepare_attack(self, all_entities):
        projectile = self.attack.attack(self, None)
        return projectile

    def get_defense_entity_hitbox(self):

        extra_width = self.width / 5 - 2
        extra_height = self.height / 5 - 1

        if self.mov_axis == [0, 1]:
            y = self.pos_y
            x = self.pos_x + 2
            width = self.width - 3
            height = int(self.height)
        elif self.mov_axis == [0, -1]:
            y = self.pos_y
            x = self.pos_x + 2
            width = self.width - 3
            height = self.height
        elif self.mov_axis == [1, 0]:
            y = self.pos_y
            x = self.pos_x
            width = int(self.width * 1/2) - 1
            height = self.height
        elif self.mov_axis == [-1, 0]:
            width = int(self.width * 2/3) - 1
            height = self.height
            y = self.pos_y + 1
            x = self.pos_x + (self.width - width) - 2
        else:
            raise ValueError('mov_axis must be one of the cardinal axis')

        hitbox = RectangleHitbox(x + extra_width, y + extra_height, width - extra_width, height - extra_height)

        return hitbox

    def initialize_projectile(self, proj_width, proj_height):
        projectile_x = None
        projectile_y = None
        if self.mov_axis == [1, 0]:
            if self.first_attack:
                projectile_x = self.pos_x + self.defense_hitbox.hitbox.width - proj_width
            else:
                projectile_x = self.pos_x + self.defense_hitbox.hitbox.width - 2 * proj_width
            projectile_y = self.pos_y + 3 / 4 * self.defense_hitbox.hitbox.height - proj_height
        elif self.mov_axis == [-1, 0]:
            if self.first_attack:
                projectile_x = self.pos_x - proj_width
            else:
                projectile_x = self.pos_x + proj_width
            projectile_y = self.pos_y + 3 / 4 * self.defense_hitbox.hitbox.height - proj_height
        elif self.mov_axis == [0, 1]:
            projectile_x = self.pos_x + self.defense_hitbox.hitbox.width - proj_width
            projectile_y = self.pos_y + self.defense_hitbox.hitbox.height
        elif self.mov_axis == [0, -1]:
            projectile_x = self.pos_x
            projectile_y = self.pos_y + proj_height
        else:
            ValueError('mov_axis must belong to [[1, 0], [-1, 0], [0, 1], [0, -1]]')

        return projectile_x, projectile_y
