from abc import ABC, abstractmethod

from scripts.dungeon.projectiles import Projectile
from scripts.utils import collision_between_two_objects


class Attack(ABC):

    def attack(self, attacker, defender):
        if attacker.attacking and attacker.attack_cooldown == attacker.max_attack_cooldown:
            damage = self.calc_damage(attacker)
            projectile = self.make_attack(attacker, defender, damage)
            return projectile

    @abstractmethod
    def make_attack(self, attacker, defender, damage):
        pass

    def calc_damage(self, attacker):
        return attacker.damage


class MeleeAttack(Attack):

    def make_attack(self, attacker, defender, damage):
        projectile = Projectile(axis=[0, 0], damage=damage, owner=attacker, lifetime=1, width=attacker.width,
                                height=attacker.height, vel=0, drawable=False)
        return projectile


class MovAxisDistanceAttack(Attack):

    def make_attack(self, attacker, defender, damage):
        projectile = Projectile(axis=attacker.mov_axis, damage=damage, owner=attacker, element=attacker.element)
        return projectile


class ToTheTargetAxisDistanceAttack(Attack):

    def make_attack(self, attacker, defender, damage):
        proj_x_axis = int(defender.defense_hitbox.center_x - attacker.attack_hitbox.center_x)
        proj_y_axis = int(defender.defense_hitbox.center_y - attacker.attack_hitbox.center_y)

        module_proj_axis = (proj_x_axis**2 + proj_y_axis**2)**(1 / 2)
        norm_proj_axis = [proj_x_axis / module_proj_axis, proj_y_axis / module_proj_axis]
        projectile = Projectile(axis=norm_proj_axis, damage=damage, owner=attacker, element=attacker.element)
        return projectile


class AttackDecorator(Attack):

    _attack_behaviour: Attack = None

    def __init__(self, attack_behaviour: Attack) -> None:
        self._attack_behaviour = attack_behaviour

    @property
    def attack_behaviour(self) -> Attack:
        return self._attack_behaviour

    def make_attack(self, attacker, defender, damage):
        return self._attack_behaviour.make_attack(attacker, defender, damage)

    def calc_damage(self, attacker):
        return self._attack_behaviour.calc_damage(attacker)


class AttackWhenVision(AttackDecorator):
    def make_attack(self, attacker, defender, damage):
        if collision_between_two_objects(attacker.vision_hitbox.hitbox, defender.defense_hitbox.hitbox):
            return self._attack_behaviour.make_attack(attacker, defender, damage)
        else:
            return None
