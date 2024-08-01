import pathlib
import os
import pygame
import scripts.utils as utils


# -------------------------------------- Entity Variables ----------------------------------------
pygame.init()

general_path = pathlib.Path(os.path.dirname(__file__)).parent
general_path = utils.resource_path(general_path)

pj_constants = utils.get_pj_constants(os.path.join(general_path, 'configurations'))
enemy_constants = utils.get_enemy_constants(os.path.join(general_path, 'configurations'))

projectiles_constants = utils.get_projectiles_constants(os.path.join(general_path, 'configurations'))

# -------------------------------------------- Display -----------------------------------------------

(WIN_X, WIN_Y, DUN_WIN_X, DUN_WIN_Y, WIN_INF_BORDER_X, WIN_INF_BORDER_Y, DUN_BORDER_X,
 DUN_BORDER_Y) = utils.get_screen_constants(os.path.join(general_path, 'configurations'))

dyn_params = utils.load_dyn_params(os.path.join(general_path, 'configurations'))

monitor_size = [pygame.display.Info().current_w, pygame.display.Info().current_h]
screen_sizes = [(2 * WIN_X, 2 * WIN_Y), (3 * WIN_X, 3 * WIN_Y), (4 * WIN_X, 4 * WIN_Y)]
if 5 * WIN_X <= monitor_size[0] and 5 * WIN_Y <= monitor_size[1]:
    screen_sizes.append((5 * WIN_X, 5 * WIN_Y))

pos_screen_size = dyn_params['screen']['pos_screen_size']
# The firsts dimension by default
first_win_x = screen_sizes[pos_screen_size][0]
first_win_y = screen_sizes[pos_screen_size][1]

first_screen_loc_x = monitor_size[0] / 2 - screen_sizes[-1][0] / 2
first_screen_loc_y = monitor_size[1] / 2 - screen_sizes[-1][1] / 2

os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (first_screen_loc_x, first_screen_loc_y)

screen = pygame.display.set_mode((first_win_x, first_win_y), pygame.RESIZABLE)

pygame.font.init()
myfont = pygame.font.SysFont('arial', 30)

FPS = 30

n_pjs = 1

# ----------------------------------------------- Animation ------------------------------------------------------
img_path = os.path.join(general_path, 'Images')

enemies_img_path = os.path.join(img_path, 'enemies')

basic_element_list = ['fire', 'water', 'darkness', 'light']
element_list = basic_element_list

logo_img = pygame.image.load(os.path.join(img_path, 'logo.ico')).convert_alpha()
pygame.display.set_icon(logo_img)

dict_actions = {action_type: {(0, -1): 'arriba', (0, 1): 'abajo', (1, 0): 'derecha',
                (-1, 0): 'izquierda'} for action_type in ['caminar_atacar', 'caminar', 'parada', 'atacar']}

# Pj

pj_animation_database = utils.load_individual_entity_animation_database(os.path.join(img_path, "protagonista"),
                                                                        dict_actions, 4)

enemy_animation_database = utils.load_enemy_animation_database(general_path, enemies_img_path, dict_actions)

# Background

bg_path = os.path.join(img_path, 'fondos')

bg_element_list = element_list + ['tutorial']

bg_img_database = {element: {'normal_bg': pygame.image.load(os.path.join(bg_path, element,
                                                                         'mazmorra.png')).convert_alpha(),
                             'door': {'open': pygame.image.load(os.path.join(bg_path, element,
                                                                             'mazmorra_puerta.png')).convert_alpha(),
                                      'locked': pygame.image.load(os.path.join(bg_path, element,
                                                                               'mazmorra_puerta.png')).convert_alpha()
                                      },
                             'boss_bg': pygame.image.load(os.path.join(bg_path, element,
                                                                       'boss_mazmorra.png')).convert_alpha()}
                   for element in bg_element_list}

# Projectiles

projectile_element_list = element_list + ['air']

projectile_path = os.path.join(img_path, 'projectiles')
projectile_img_database = {elem: utils.load_animation(projectile_path, elem, 'frames',
                                                      frame_duration=projectiles_constants[elem]['frame_duration'])
                           for elem in projectile_element_list}


# ------------------------------------------------ Music -------------------------------------------

music_vol = dyn_params['music']['music_vol']

vol_ratio_hit, vol_ratio_mons_dead, vol_ratio_att = utils.get_music_constants(os.path.join(general_path,
                                                                                           'configurations'))

pygame.mixer.music.load(os.path.join(general_path, 'Music', 'PRUEBA_AGOSTO_LOOP_retocada.mp3'))
pygame.mixer.music.play(-1)  # -1 infinitely
pygame.mixer.pre_init(channels=1)  # channel 1:mono 2:stereo
pygame.mixer.music.set_volume(music_vol)

hit_sound = pygame.mixer.Sound(os.path.join(general_path, 'Music', 'Resto_vida.wav'))
hit_sound.set_volume(vol_ratio_hit*music_vol)
monster_dead_sound = pygame.mixer.Sound(os.path.join(general_path, 'Music', 'Muerte_monstruo.wav'))
monster_dead_sound.set_volume(vol_ratio_mons_dead*music_vol)
attack_sound = pygame.mixer.Sound(os.path.join(general_path, 'Music', 'desenvainar_espada.wav'))
attack_sound.set_volume(vol_ratio_att*music_vol)

# --------------------------------------------- Fonts ----------------------------------

fonts_mapper = {'arial': os.path.join(general_path, 'Fonts', 'Arial.ttf')}
