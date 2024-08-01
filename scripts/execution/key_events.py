import os
import sys
from abc import ABC, abstractmethod
from typing import Optional
import pygame

from scripts import utils
from scripts.variables import screen_sizes, general_path


class KeyboardEvents(ABC):

    def __init__(self):
        self.keys_kept_pressed = None
        self.get_iter_keys()
        self.events = pygame.event.get()

    def get_iter_keys(self):
        self.keys_kept_pressed = pygame.key.get_pressed()

    def key_map(self):
        self.get_iter_keys()
        run_output = self.run_key_map()
        return run_output

    def run_key_map(self):
        run_output = self.key_events()
        self.pressed_keys()
        return run_output

    def key_events(self) -> Optional[dict]:
        from scripts.execution.run import Run

        run_output = None

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                self.save_run_parameters()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                run_output = self.keydown_events(event)
            elif event.type == pygame.VIDEORESIZE:
                Run.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        return run_output

    @abstractmethod
    def pressed_keys(self):
        pass

    @abstractmethod
    def keydown_events(self, event):
        pass

    def save_run_parameters(self):
        pass


class DungeonKeyboardEvents(KeyboardEvents):

    def __init__(self, dung_run):
        super(DungeonKeyboardEvents, self).__init__()
        self.pj = dung_run.pj
        self.dung_run = dung_run

    def pressed_keys(self):
        self.key_volume()
        self.keys_pj_movement()

    def key_volume(self):
        if self.keys_kept_pressed[pygame.K_v]:
            self.dung_run.music_vol += 0.1
            self.dung_run.music_vol = min(1, self.dung_run.music_vol)
            pygame.mixer.music.set_volume(self.dung_run.music_vol)
            pygame.time.delay(200)
        elif self.keys_kept_pressed[pygame.K_b]:
            self.dung_run.music_vol -= 0.1
            self.dung_run.music_vol = max(0, self.dung_run.music_vol)
            pygame.mixer.music.set_volume(self.dung_run.music_vol)
            pygame.time.delay(200)

    def keys_pj_movement(self):
        if self.keys_kept_pressed[pygame.K_UP] or self.keys_kept_pressed[pygame.K_w]:
            self.pj.axis[1] = -1
            self.pj.moving = True
        if self.keys_kept_pressed[pygame.K_DOWN] or self.keys_kept_pressed[pygame.K_s]:
            self.pj.axis[1] = 1
            self.pj.moving = True
        if self.keys_kept_pressed[pygame.K_RIGHT] or self.keys_kept_pressed[pygame.K_d]:
            self.pj.axis[0] = 1
            self.pj.moving = True
        if self.keys_kept_pressed[pygame.K_LEFT] or self.keys_kept_pressed[pygame.K_a]:
            self.pj.axis[0] = -1
            self.pj.moving = True

    def keydown_events(self, event):
        if event.key == pygame.K_f:
            self.dung_run.pos_screen_size += 1
            if self.dung_run.pos_screen_size >= len(screen_sizes):
                self.dung_run.pos_screen_size = 0
            self.dung_run.screen = pygame.display.set_mode(screen_sizes[self.dung_run.pos_screen_size],
                                                           pygame.RESIZABLE)
        elif event.key == pygame.K_m:
            from scripts.execution.run import MapRun
            return self.dung_run.make_run_output(False, MapRun(self.dung_run))
            # open_map = not open_map
        elif event.key == pygame.K_i:
            # return InventoryMenuRun
            pass
            # open_invent = not open_invent

            # sword_runes_names, sword_runes = inventory_menu(sword)
        elif event.key in [pygame.K_q, pygame.K_p] and self.pj.attack_cooldown <= 0:
            # keys[pygame.K_q] or keys[pygame.K_p]
            self.pj.set_attack_attributes()

    def save_run_parameters(self):
        new_params = utils.create_params_dict(self.dung_run.pos_screen_size, self.dung_run.music_vol,
                                              floor=1, sword_runes_names=self.pj.sword.sword_runes_names,
                                              slots=self.pj.sword.slots)
        utils.save_dyn_params(os.path.join(general_path, 'configurations'), new_params)


class MapKeyboardEvents(KeyboardEvents):

    def pressed_keys(self):
        pass

    def keydown_events(self, event):

        if event.key == pygame.K_m:
            from scripts.execution.run import Run
            return Run.make_run_output(True, None)
        

class EndKeyboardEvents(KeyboardEvents):

    def pressed_keys(self):
        pass

    def keydown_events(self, event):
        if event.key == pygame.K_RETURN:
            from scripts.execution.run import Run, DungeonRun
            return Run.make_run_output(True, DungeonRun(dungeon_element='tutorial'))
