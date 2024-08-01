from abc import ABC, abstractmethod

import pygame
from scripts.variables import (WIN_X, WIN_Y, DUN_WIN_X, DUN_WIN_Y, bg_img_database, 
                               WIN_INF_BORDER_X, WIN_INF_BORDER_Y, screen_sizes, fonts_mapper)


class RunDrawHandler(ABC):

    def __init__(self, screen):
        self.screen = screen

    @staticmethod
    def set_priority_objects_order_list(pj, enemies, objects):
        objects_to_draw = objects + enemies + [pj]
        return objects_to_draw

    @abstractmethod
    def draw_run(self, **kwargs):
        pass


class DungeonDrawHandler(RunDrawHandler):
    
    def __init__(self, dungeon_run):
        super(DungeonDrawHandler, self).__init__(dungeon_run.screen)
        self.black_screen_count = 0
        self.is_crossing_door = False
        self.dungeon_run = dungeon_run
        self.dungeon_element = dungeon_run.dungeon_element

        self.dungeon_screen = None
        self.intermediate_screen = None
        self.is_map_open = False

    def draw_run(self, pj, enemies, objects):
        objects_to_draw = self.set_priority_objects_order_list(pj, enemies, objects)
        self.intermediate_screen = pygame.surface.Surface((WIN_X, WIN_Y))

        self.draw_contour_dungeon_limits()
        self.dungeon_screen = pygame.surface.Surface((DUN_WIN_X, DUN_WIN_Y))
        self.do_crossing_door(pj)
        if not pj.is_crossing_door:
            self.draw_dungeon(objects_to_draw, self.dungeon_element)

        self.intermediate_screen.blit(self.dungeon_screen, (WIN_X - DUN_WIN_X - WIN_INF_BORDER_X,
                                                            WIN_Y - DUN_WIN_Y - WIN_INF_BORDER_Y))
        self.screen.blit(pygame.transform.scale(self.intermediate_screen, self.screen.get_rect().size), (0, 0))

    def draw_contour_dungeon_limits(self):
        self.intermediate_screen.fill((255, 100, 100))

    def do_crossing_door(self, pj):
        if pj.is_crossing_door:
            self.dungeon_screen.fill((10, 10, 10))
            self.black_screen_count += 1
            pj.is_crossing_door = True
        else:
            if 0 < self.black_screen_count < 4:
                self.dungeon_screen.fill((10, 10, 10))
                self.black_screen_count += 1
                pj.is_crossing_door = True
            else:
                self.black_screen_count = 0
                pj.is_crossing_door = False

    def draw_dungeon(self, objects_to_draw, dungeon_element):
        if self.dungeon_run.is_exit_room:
            self.dungeon_screen.blit(bg_img_database[dungeon_element]['boss_bg'], (0, 0))
            self.draw_room(objects_to_draw)

        else:
            self.dungeon_screen.blit(bg_img_database[dungeon_element]['normal_bg'], (0, 0))
            self.draw_room(objects_to_draw)

    def draw_room(self, objects_to_draw):
        self.dungeon_run.current_dungeon.doors_handler.draw_doors(self.dungeon_screen)

        for obj in objects_to_draw:
            obj.draw.draw(self.dungeon_screen)


class Draw(ABC):

    def __init__(self, obj, image_database):
        self.obj = obj
        self.image_database = image_database

    @abstractmethod
    def draw(self, screen):
        pass


class NoDraw(Draw):

    def __init__(self):
        pass

    def draw(self, screen):
        pass


class DrawRectangle(Draw):

    def __init__(self, obj, image_database, color=(200, 0, 0)):
        super().__init__(obj, image_database)
        self.color = color

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.obj.draw_hitbox.hitbox, 1)


class DrawImage(Draw):

    def draw(self, screen):
        screen.blit(self.image_database, self.obj.draw_hitbox.hitbox)
        # pygame.draw.rect(screen, (0, 0, 0), self.obj.draw_hitbox.hitbox, 1)


class DrawEntityAnimation(Draw):

    def __init__(self, obj, image_database):
        super(DrawEntityAnimation, self).__init__(obj, image_database)
        self.frames = 0
        self.last_frames = 0

    def draw(self, screen):
        img, previous_frame_img = self.get_the_img()
        rect = self.fix_img_position_when_dimension_changes(img, previous_frame_img)
        self.obj.movement.move_hitboxes()
        screen.blit(img, rect)

    def get_the_img(self):
        if self.frames >= len(self.image_database[self.obj.state][tuple(self.obj.mov_axis)]):
            self.frames = 0
        if self.last_frames >= len(self.image_database[self.obj.last_state][tuple(self.obj.last_mov_axis)]):
            self.last_frames = 0

        img = self.image_database[self.obj.state][tuple(self.obj.mov_axis)][self.frames]
        previous_frame_img = self.image_database[self.obj.last_state][tuple(self.obj.last_mov_axis)][self.last_frames]
        self.last_frames = self.frames
        self.frames += 1
        return img, previous_frame_img

    def fix_img_position_when_dimension_changes(self, img, previous_frame_img):
        rect = img.get_rect()
        self.obj.width = rect.width
        self.obj.height = rect.height
        previous_rect = previous_frame_img.get_rect()
        if not (self.obj.mov_axis != [0, -1] and self.obj.attacking):
            self.obj.pos_y -= (rect.height - previous_rect.height)
        if self.obj.mov_axis == [-1, 0]:
            self.obj.pos_x -= (rect.width - previous_rect.width)
        rect.x = self.obj.pos_x
        rect.y = self.obj.pos_y
        self.obj.last_width = self.obj.width
        return rect


class DrawAnimation(Draw):

    def __init__(self, obj, image_database):
        super(DrawAnimation, self).__init__(obj, image_database)
        self.frames = 0
        self.last_frames = 0

    def draw(self, screen):
        img, previous_frame_img = self.get_the_img()
        rect = self.get_rect(img)
        self.obj.movement.move_hitboxes()
        screen.blit(img, rect)

    def get_the_img(self):
        if self.frames >= len(self.image_database):
            self.frames = 0
        if self.last_frames >= len(self.image_database):
            self.last_frames = 0

        img = self.image_database[self.frames]
        previous_frame_img = self.image_database[self.last_frames]
        self.last_frames = self.frames
        self.frames += 1
        return img, previous_frame_img

    def get_rect(self, img):
        rect = img.get_rect()
        rect.x = self.obj.pos_x
        rect.y = self.obj.pos_y
        return rect


class DrawLifeBar(Draw):

    def __init__(self, obj):
        super(DrawLifeBar, self).__init__(obj, image_database=None)
        self.hp_width = self.obj.width

    def draw(self, screen):
        # TODO: change the position for the pj?
        # Barras de vida
        hp_barra = pygame.Rect(self.obj.pos_x + 1, self.obj.pos_y - 4,
                               int(self.hp_width * (self.obj.hp / self.obj.max_hp)), 1)
        hp_barra_black = pygame.Rect(self.obj.pos_x, self.obj.pos_y - 5, self.hp_width + 2, 3)

        pygame.draw.rect(screen, (0, 0, 0), hp_barra_black, 1)
        pygame.draw.rect(screen, (0, 200, 0), hp_barra, 1)


class DrawAnimationEntityWithLifeBar(Draw):

    def __init__(self, obj, animation_database) -> None:
        super(DrawAnimationEntityWithLifeBar, self).__init__(obj, animation_database)
        self.draw_animation = DrawEntityAnimation(obj, animation_database)
        self.draw_life_bar = DrawLifeBar(obj)

    def draw(self, screen):
        self.draw_animation.draw(screen)
        self.draw_life_bar.draw(screen)


class DrawDecorator(Draw):

    _draw_behaviour: Draw = None

    def __init__(self, obj, image_database, draw_behaviour) -> None:
        super(DrawDecorator, self).__init__(obj, image_database)
        self._draw_behaviour = draw_behaviour(obj, image_database)

    @property
    def draw_behaviour(self) -> Draw:
        return self._draw_behaviour

    def draw(self, screen):
        return self._draw_behaviour.draw(screen)


class DrawSuppEntityHitbox(DrawDecorator):

    def __init__(self, obj, animation_database):
        super(DrawSuppEntityHitbox, self).__init__(obj, animation_database, DrawAnimationEntityWithLifeBar)

    def draw(self, screen):
        self.draw_hitboxes_supp(screen)
        self._draw_behaviour.draw(screen)

    def draw_hitboxes_supp(self, screen):
        # TODO: remove when finish the tests
        pygame.draw.rect(screen, (0, 255, 0), self.obj.draw_hitbox.hitbox, 1)
        pygame.draw.rect(screen, (255, 0, 0), self.obj.attack_hitbox.hitbox, 1)
        # pygame.draw.rect(screen, (0, 0, 255), self.obj.door_hitbox.hitbox, 1)


class DrawTextScreen(Draw):

    def __init__(self, obj, image_database):
        super().__init__(obj, image_database)
        self.font = pygame.font.Font(fonts_mapper['arial'], 25)
    
    def draw(self, screen):
        label = self.font.render(self.obj.text + '. Press enter to restart the game.', 1, (255, 255, 255))
        window_x, window_y = screen_sizes[self.obj.pos_screen_size]
        screen.fill((0, 0, 0))
        screen.blit(label, (window_x / 2 - label.get_width() / 2, window_y / 2 - label.get_height() / 2))
