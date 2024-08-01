import pygame
import os
import configparser
import json

import pathlib
from glob import glob

from typing import Union
from scripts.geometric_forms import Circle


def load_animation(path, folder_type, folder_dir, frame_duration):
    animation_frame_data = []
    img_dir = os.path.join(path, folder_type, folder_dir)
    images_path = glob(os.path.join(img_dir, "*.png"))
    for img_path in images_path:
        animation_image = pygame.image.load(img_path).convert_alpha()
        for i in range(frame_duration):
            animation_frame_data.append(animation_image.copy())
    return animation_frame_data


def argsort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)


def collision_between_two_objects(hitbox1: Union[pygame.Rect, Circle], hitbox2: Union[pygame.Rect, Circle]):
    if isinstance(hitbox1, pygame.Rect) and isinstance(hitbox2, pygame.Rect):
        return hitbox1.colliderect(hitbox2)
    elif isinstance(hitbox1, pygame.Rect) and isinstance(hitbox2, Circle):
        return collision_rect_circ(hitbox1, hitbox2)
    elif isinstance(hitbox1, Circle) and isinstance(hitbox2, pygame.Rect):
        return collision_rect_circ(hitbox2, hitbox1)
    else:
        raise NotImplementedError('Collision between two circles has not been implemented')


def collision_rect_circ(rect_hitbox: pygame.Rect, circ_hitbox: Circle) -> bool:  # circle definition
    """ Detect collision between a rectangle and circle. """
    rleft = rect_hitbox.x
    rtop = rect_hitbox.y
    width = rect_hitbox.width
    height = rect_hitbox.height
    center_x = circ_hitbox.center_x
    center_y = circ_hitbox.center_y
    radius = circ_hitbox.radius
    # complete boundbox of the rectangle
    rright, rbottom = rleft + width/2, rtop + height/2

    # bounding box of the circle
    cleft, ctop = center_x-radius, center_y-radius
    cright, cbottom = center_x+radius, center_y+radius

    # trivial reject if bounding boxes do not intersect
    if rright < cleft or rleft > cright or rbottom < ctop or rtop > cbottom:
        return False  # no collision possible

    else:
        return True


def get_config_parser_generic_parameters(path):
    raw_configparser = configparser.RawConfigParser()
    config_path = os.path.join(path, "configuration_file.cfg")
    raw_configparser.read(config_path)
    return raw_configparser


def get_pj_constants(path):
    raw_configparser = get_config_parser_generic_parameters(path)
    searcher = dict(raw_configparser.items("PJ"))
    constants = {key: eval(value) for key, value in searcher.items()}
    return constants


def get_enemy_constants(path):
    enemies_path = glob("Images/enemies/*", recursive=False)
    constants = {}
    for enemy_path in enemies_path:
        enemy_name = enemy_path.split(os.sep)[-1]
        raw_configparser = get_config_parser_generic_parameters(path)
        searcher = dict(raw_configparser.items(enemy_name.upper()))

        enemy_constants = {key: eval(value) for key, value in searcher.items()}
        constants[enemy_name] = enemy_constants
    return constants


def load_individual_entity_animation_database(image_directory, dict_actions, frame_duration):
    animation_database = {}
    for folder_type in dict_actions.keys():
        animation_dir_database = {}
        for directory in dict_actions[folder_type].keys():
            folder_dir = dict_actions[folder_type][directory]
            animation_dir_database[directory] = load_animation(image_directory, folder_type, folder_dir,
                                                               frame_duration)
        animation_database[folder_type] = animation_dir_database

    return animation_database


def load_enemy_animation_database(general_path, enemies_img_path, dict_actions):
    enemies_path = glob("Images/enemies/*", recursive=False)
    enemy_animation_database = {}
    enemy_constants = get_enemy_constants(os.path.join(general_path, 'configurations'))
    for enemy_path in enemies_path:
        enemy_name = os.path.split(enemy_path)[-1]

        frame_duration = enemy_constants[enemy_name]["frame_duration"]
        animation_database = load_individual_entity_animation_database(os.path.join(enemies_img_path, enemy_name),
                                                                       dict_actions, frame_duration)
        enemy_animation_database[enemy_name] = animation_database

    return enemy_animation_database


def get_projectiles_constants(path):
    raw_configparser = get_config_parser_generic_parameters(path)

    elements = ['air', 'fire', 'water', 'darkness', 'light']

    constants = {}
    for element in elements:
        searcher = dict(raw_configparser.items(element.upper()))
        elem_constants = {key: eval(value) for key, value in searcher.items()}
        constants[element] = elem_constants

    return constants


def get_screen_constants(path):
    raw_configparser = get_config_parser_generic_parameters(path)
    searcher = dict(raw_configparser.items("SCREEN"))
    win_x = int(searcher.get("win_x"))
    win_y = int(searcher.get("win_y"))
    dun_win_x = int(searcher.get("dun_win_x"))
    dun_win_y = int(searcher.get("dun_win_y"))
    win_inf_border_x = int(searcher.get("win_inf_border_x"))
    win_inf_border_y = int(searcher.get("win_inf_border_y"))
    dun_border_x = int(searcher.get("dun_border_x"))
    dun_border_y = int(searcher.get("dun_border_y"))
    return win_x, win_y, dun_win_x, dun_win_y, win_inf_border_x, win_inf_border_y, dun_border_x, dun_border_y


def get_music_constants(path):
    raw_configparser = get_config_parser_generic_parameters(path)
    searcher = dict(raw_configparser.items("MUSIC"))
    vol_ratio_hit = float(searcher.get("vol_ratio_hit"))
    vol_ratio_mons_dead = float(searcher.get("vol_ratio_mons_dead"))
    vol_ratio_att = float(searcher.get("vol_ratio_att"))
    return vol_ratio_hit, vol_ratio_mons_dead, vol_ratio_att


def save_dyn_params(path, parameters):
    params_path = os.path.join(path, 'dynamic_parameters.json')
    with open(params_path, 'w') as json_file:
        json.dump(parameters, json_file)


def load_dyn_params(path):
    params_path = os.path.join(path, 'dynamic_parameters.json')
    with open(params_path, 'r') as json_file:
        parameters = json.load(json_file)
    return parameters


def create_params_dict(pos_screen_size, music_vol, floor, sword_runes_names, slots):
    params = {'screen': {'pos_screen_size': pos_screen_size},
              'music': {'music_vol': music_vol},
              'dungeon': {'floor': floor},
              'sword': {'runes_names': sword_runes_names, 'slots': slots}}
    return params


def create_new_dyn_params_json():
    general_path = pathlib.Path(os.path.dirname(__file__))
    pos_screen_size = 0
    music_vol = 0.6

    new_params = create_params_dict(pos_screen_size, music_vol, floor=1, sword_runes_names="", slots=3)
    save_dyn_params(os.path.join(general_path, 'configurations'), new_params)


def resource_path(relative):
    return os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative
    )


def line_intersection(line1, line2):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)
    if div == 0:
        raise Exception('lines do not intersect')

    d = (det(*line1), det(*line2))
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return x, y
