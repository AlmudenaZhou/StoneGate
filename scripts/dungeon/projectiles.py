from scripts.draw import DrawAnimation, NoDraw
from scripts.entity.movement import Movement, BaseMovement
from scripts.objects import Object
from scripts.utils import collision_between_two_objects, argsort
from scripts.variables import n_pjs, projectiles_constants, projectile_img_database, DUN_WIN_Y, DUN_WIN_X


class Projectile(Object):
    def __init__(self, axis, damage: int, owner, element: str = None, lifetime: int = None,
                 movement: Movement = None, width=None, height=None, vel=None, drawable=True):
        self.width = width if width is not None else projectiles_constants[element]['width']
        self.height = height if height is not None else projectiles_constants[element]['height']

        pos_x, pos_y = owner.initialize_projectile(self.width, self.height)

        super().__init__(pos_x, pos_y, self.width, self.height, axis)
        self.damage = damage if damage is not None else projectiles_constants[element]['damage']
        self.movement = movement if movement is not None else BaseMovement(self)
        self.lifetime = lifetime if lifetime is not None else projectiles_constants[element]['lifetime']
        self.owner = owner
        self.attack_hitbox = self.draw_hitbox

        self.vel = vel if vel is not None else projectiles_constants[element]['vel']
        self.mov_axis = self.axis

        if not drawable:
            self.draw = NoDraw()
        else:
            self.draw = DrawAnimation(self, image_database=projectile_img_database[element])

    def turn(self, all_entities):
        self.movement.move(self)
        self.lifetime -= 1
        if self.check_projectile_outside_screen():
            return True
        elif self.check_entity_collision(all_entities):
            return True
        elif self.lifetime <= 0:
            return True

    def check_projectile_outside_screen(self):
        if self.pos_x < 0 or self.pos_x > DUN_WIN_X:
            return True
        elif self.pos_y < 0 or self.pos_y > DUN_WIN_Y:
            return True
        return False

    def check_entity_collision(self, all_entities):
        from scripts.entity.entity import Pj
        potential_damaged_entities = all_entities[n_pjs:] if isinstance(self.owner, Pj) else all_entities[:n_pjs]

        distance_to_entities = [((self.pos_x - entity.pos_x)**2 + (self.pos_y - entity.pos_y)**2)**(1/2)
                                for entity in potential_damaged_entities]

        entities_index = argsort(distance_to_entities)
        potential_damaged_entities = [potential_damaged_entities[i] for i in entities_index]
        for entity in potential_damaged_entities:
            if collision_between_two_objects(entity.defense_hitbox.hitbox, self.attack_hitbox.hitbox):
                entity.hp -= self.damage
                return True
        return False
