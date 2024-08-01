import pygame

from scripts.draw import DrawImage, DrawRectangle
from scripts.dungeon.hitboxes import RectangleHitbox
from scripts.magic import WordMagic, magic_dict
from scripts.utils import collision_between_two_objects
from scripts.variables import projectile_element_list, bg_img_database


class Object:

    def __init__(self, pos_x, pos_y, width, height, axis):

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.axis = axis
        self.draw_hitbox = RectangleHitbox(pos_x, pos_y, width, height)
        self.img_database = None
        self.frames = 0
        self.draw = DrawRectangle(self, self.img_database)


class Door:

    # TODO: add lock_door_img
    def __init__(self, pos_x, pos_y, width, height, id_number, mov, database_img, rotation_degree, state='open'):
        """
        :param pos_x:
        :param pos_y:
        :param width:
        :param height:
        :param id_number:
        :param mov:
        :param database_img:
        :param rotation_degree:
        :param state: can be open, lock
        """
        self.pos_x = pos_x
        self.pos_y = pos_y

        self.width = width
        self.height = height
        self.hitbox = RectangleHitbox(pos_x, pos_y, width, height)

        self.id_number = id_number
        self.state = state
        self.exist = False
        self.database_img = database_img
        self.rotation_degree = rotation_degree

        img = self.database_img[self.state]
        final_img = pygame.transform.rotate(img, self.rotation_degree)
        self.draw = DrawImage(self, final_img)  # TODO: make dynamic draw image (change with the state)

        self.draw_hitbox = RectangleHitbox(pos_x, pos_y, width, height)

        self.mov = mov
        self.opposite_door = None


class Doors:
    # TODO: add lock_door_img
    def __init__(self, dungeon_element):
        self.door_img_database = bg_img_database[dungeon_element]['door']
        self.doors = []

    def create_doors(self, x, y):
        rect = self.door_img_database['open'].get_rect()
        width = rect.height
        height = rect.width
        door1 = Door(pos_x=int(x / 2) - height / 2, pos_y=y - width - 6, width=height, height=width, id_number=0,
                     mov=(0, 1), rotation_degree=180, database_img=self.door_img_database)
        door2 = Door(pos_x=6, pos_y=int(y / 2) - height / 2, width=width, height=height, id_number=1, mov=(-1, 0),
                     rotation_degree=90, database_img=self.door_img_database)
        door3 = Door(pos_x=int(x / 2) - height / 2, pos_y=6, width=height, height=width, id_number=2, mov=(0, -1),
                     rotation_degree=0, database_img=self.door_img_database)
        door4 = Door(pos_x=x - width - 6, pos_y=int(y / 2) - height / 2, width=width, height=height, id_number=0,
                     mov=(1, 0), rotation_degree=270, database_img=self.door_img_database)

        door1.opposite_door = door3
        door2.opposite_door = door4
        door3.opposite_door = door1
        door4.opposite_door = door2

        self.doors.append(door1)
        self.doors.append(door2)
        self.doors.append(door3)
        self.doors.append(door4)

    def draw_doors(self, screen):
        for idx, door in enumerate(self.doors):
            if door.state == 'open' and door.exist:
                door.draw.draw(screen)

    def door_check(self, pj):
        door_conditions = (not pj.attacking and not pj.is_crossing_door and pj.crossing_door_count > 30)
        pj.crossing_door_count += 1
        if door_conditions:
            for door in self.doors:
                if door.state == 'open' and door.exist:
                    if collision_between_two_objects(door.hitbox.hitbox, pj.door_hitbox.hitbox):
                        pj.is_crossing_door = True
                        pj.crossing_door_count = 0
                        return door
        return False


class Sword:
    def __init__(self, sword_runes_names, slots):
        self.sword_runes_names = sword_runes_names
        self.element = 'air'
        self.runes = self.get_sword_runes_from_name(sword_runes_names)
        self.extra_width = 0
        self.extra_height = 0
        self.extra_duration = 0
        self.extra_vel = 0
        self.extra_damage = 0
        self.effect = None
        self.slots = slots
        self.change_runes(sword_runes_names, self.runes)

    def initialize_sword_params(self):
        self.extra_width = 0
        self.extra_height = 0
        self.extra_duration = 0
        self.extra_vel = 0
        self.extra_damage = 0
        self.effect = None

    def change_runes(self, sword_runes_names, new_runes):
        # TODO: change this function if there is going to be element combinations
        self.initialize_sword_params()
        self.runes = new_runes
        element = set(sword_runes_names).intersection(set(projectile_element_list))
        assert len(element) == 1, "it can only have one element"
        element = list(element)[0]
        self.element = element

        if self.slots > 1:
            element_rune_index = sword_runes_names.index(element)
            effect_runes = [x for i, x in enumerate(new_runes) if i != element_rune_index]
        else:
            effect_runes = []
        for effect_rune in effect_runes:
            WordMagic.magic_effects(self, effect_rune)

    @staticmethod
    def get_sword_runes_from_name(sword_runes_names):
        sword_runes = []
        for rune in sword_runes_names:
            sword_runes.append(magic_dict[rune])
        return sword_runes
