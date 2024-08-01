from abc import ABC, abstractmethod
from scripts.dungeon.hitboxes import CircleHitbox
from scripts.entity.attack import AttackWhenVision, ToTheTargetAxisDistanceAttack, MeleeAttack
from scripts.entity.entity import Entity
from scripts.entity.movement import NoMovement, MovementTowardsSomething
from scripts.variables import enemy_constants, enemy_animation_database


class Enemy(Entity, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, animation_database=enemy_animation_database[self.name],
                         **kwargs, **enemy_constants[self.name])
        self.moving = True
        self.attacking = True

    @property
    @abstractmethod
    def name(self):
        raise NotImplementedError

    def prepare_attack(self, all_entities):
        projectile = self.attack.attack(self, all_entities[0])
        return projectile


class Moco(Enemy):

    def __init__(self, element, *args, **kwargs):
        self._name = "moco"
        super().__init__(*args, **kwargs)
        self.element = element
        self.movement = NoMovement(self)

        self.attack = AttackWhenVision(ToTheTargetAxisDistanceAttack())
        self.max_attack_cooldown += 20
        self.vision_hitbox = CircleHitbox(self.pos_x, self.pos_y, self.width, self.height,
                                          enemy_constants[self.name]['vision'])

    @property
    def name(self):
        return self._name

    def initialize_projectile(self, proj_width, proj_height):
        projectile_x = self.pos_x + self.width / 2
        projectile_y = self.pos_y + self.height / 2
        return projectile_x, projectile_y

    def set_attributes_before_turn(self):
        if self.attack_cooldown < 0:
            self.set_attack_attributes()


class Tostada(Enemy):

    def __init__(self, *args, **kwargs):
        self._name = 'tostada'
        super().__init__(*args, **kwargs)
        self.movement = MovementTowardsSomething(self)

        self.attack = MeleeAttack()

    @property
    def name(self):
        return self._name

    def set_attributes_before_turn(self):
        self.moving = False
        if self.attack_cooldown < 0:
            self.set_attack_attributes()

    def initialize_projectile(self, proj_width, proj_height):
        return self.pos_x, self.pos_y


class Boca(Enemy):

    def __init__(self, *args, **kwargs):
        self._name = 'boca'
        super().__init__(*args, **kwargs)
        self.movement = MovementTowardsSomething(self)

        self.attack = MeleeAttack()

    @property
    def name(self):
        return self._name

    def set_attributes_before_turn(self):
        self.moving = False
        if self.attack_cooldown < 0:
            self.set_attack_attributes()

    def initialize_projectile(self, proj_width, proj_height):
        return self.pos_x, self.pos_y


class Conejo(Enemy):

    def __init__(self, *args, **kwargs):
        self._name = 'conejo'
        super().__init__(*args, **kwargs)
        self.movement = MovementTowardsSomething(self)

        self.attack = MeleeAttack()

    @property
    def name(self):
        return self._name

    def set_attributes_before_turn(self):
        self.moving = False
        if self.attack_cooldown < 0:
            self.set_attack_attributes()

    def initialize_projectile(self, proj_width, proj_height):
        return self.pos_x, self.pos_y


class Boss(Enemy):

    def __init__(self, element, *args, **kwargs):
        self._name = "boss"
        super().__init__(*args, **kwargs)
        self.element = element
        self.movement = NoMovement(self)

        self.attack = AttackWhenVision(ToTheTargetAxisDistanceAttack())
        self.max_attack_cooldown += 20
        self.vision_hitbox = CircleHitbox(self.pos_x, self.pos_y, self.width, self.height,
                                          enemy_constants[self.name]['vision'])

    @property
    def name(self):
        return self._name

    def initialize_projectile(self, proj_width, proj_height):
        projectile_x = self.pos_x + self.width / 2
        projectile_y = self.pos_y + self.height / 2
        return projectile_x, projectile_y

    def set_attributes_before_turn(self):
        if self.attack_cooldown < 0:
            self.set_attack_attributes()
