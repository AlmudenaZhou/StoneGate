from __future__ import annotations

from collections import deque
from abc import ABC, abstractmethod
from typing import Optional

import pygame

from scripts.draw import DrawTextScreen, DungeonDrawHandler
from scripts.entity.entity import Pj
from scripts.execution.key_events import DungeonKeyboardEvents, EndKeyboardEvents, MapKeyboardEvents
from scripts.map import Map
from scripts.objects import Sword
from scripts.variables import (WIN_X, WIN_Y, screen_sizes, dyn_params, pos_screen_size, DUN_WIN_X, DUN_WIN_Y,
                               pj_animation_database, pj_constants, FPS, WIN_INF_BORDER_X, WIN_INF_BORDER_Y)


class RunHandler:
    def __init__(self):
        self.run_stack = deque()

    def queue_run(self, run_obj):
        self.run_stack.append(run_obj)

    def dequeue_run(self):
        if len(self.run_stack) > 0:
            self.run_stack.pop()
        else:
            print('There is no run stacked')

    def shut_down(self):
        self.run_stack.clear()


class MainRun:
    def __init__(self):
        self.handler = RunHandler()
        self.handler.queue_run(DungeonRun(dungeon_element='tutorial'))
        self.stop = False
        self.run_stack = self.handler.run_stack

    def main_run(self):
        while not self.stop:
            run_return = self.run_stack[-1].run_iteration()
            if run_return is not None:
                # If True, it replaces the previous run
                if run_return['is_dropped']:
                    self.handler.dequeue_run()
                if run_return['run_instance'] is not None:
                    self.handler.queue_run(run_return['run_instance'])


class Run(ABC):

    pos_screen_size = pos_screen_size
    screen = pygame.display.set_mode(screen_sizes[pos_screen_size], pygame.RESIZABLE)
    music_vol = dyn_params['music']['music_vol']
    clock = pygame.time.Clock()
    keyboard_handler = None

    def run_iteration(self) -> dict:
        self.clock.tick(FPS)
        run_output = self.keyboard_handler.key_map()

        sp_run_output = self.specific_run_iteration()
        if sp_run_output:
            run_output = sp_run_output

        if run_output is not None:
            return run_output

    @abstractmethod
    def specific_run_iteration(self):
        pass

    @staticmethod
    def make_run_output(is_dropped: bool, run_instance: Optional[Run]) -> dict:
        return {'is_dropped': is_dropped, 'run_instance': run_instance}


class DungeonRun(Run):

    def __init__(self, dungeon_element: str):
        # Probé a no hacer el copy y ponerlo directamente y petaba no sé por qué.
        # Probar a quitarlo cuando se acabe el refactor
        self.fake_screen = pygame.display.set_mode((WIN_X, WIN_Y), pygame.RESIZABLE).copy()
        Run.screen = pygame.display.set_mode(screen_sizes[self.pos_screen_size], pygame.RESIZABLE)

        self.pj = self.init_pj()

        self.dungeon_element = dungeon_element

        self.level_map = self.init_map()

        self.current_dungeon = self.level_map.dungeons[self.level_map.entry_room_key]
        self.projectiles = None
        self.objects = None
        self.entities = None
        self.update_dungeon_attributes()
        self.is_exit_room = False

        self.black_screen_count = 0
        self.keyboard_handler = DungeonKeyboardEvents(self)
        self.draw_handler = DungeonDrawHandler(self)

    @staticmethod
    def init_pj():
        sword_runes_names = dyn_params['sword']['runes_names']
        slots = dyn_params['sword']['slots']
        sword = Sword(sword_runes_names, slots)
        pj = Pj(pos_x=DUN_WIN_X - 100, pos_y=DUN_WIN_Y - 100, sword=sword, animation_database=pj_animation_database,
                **pj_constants)
        return pj

    def update_dungeon_attributes(self):
        self.projectiles = []
        self.objects = self.projectiles

    def init_map(self):
        level_map = Map(dyn_params['dungeon'], self.dungeon_element)
        level_map.generate_level_map()
        return level_map

    def specific_run_iteration(self):
        self.pj.is_crossing_door = False
        pj_dead = self.alive_check()

        if pj_dead or (self.is_exit_room and len(self.current_dungeon.enemies) == 0):
            return self.make_run_output(is_dropped=True, run_instance=EndMenuRun(pj_dead=pj_dead))

        self.entities = [self.pj] + self.current_dungeon.enemies

        for projectile in self.projectiles:
            is_deleted = projectile.turn(self.entities)
            if is_deleted:
                self.projectiles.remove(projectile)

        for entity in self.entities:
            projectile = entity.turn(self.entities)
            if projectile is not None:
                self.projectiles.append(projectile)

        door = self.current_dungeon.doors_handler.door_check(self.pj)
        if door:
            self.pj.is_crossing_door = True
            self.set_new_room(door)

        self.draw_handler.draw_run(self.pj, self.current_dungeon.enemies, self.objects)
        pygame.display.update()

    def set_new_room(self, door):
        self.change_dungeon(door)
        self.pj.cross_door(door.opposite_door)
        self.level_map.visible_rooms.add(self.current_dungeon.key)
        self.update_dungeon_attributes()

    def change_dungeon(self, door):
        new_dungeon_key = self.current_dungeon.key[0] + door.mov[0], self.current_dungeon.key[1] + door.mov[1]
        if new_dungeon_key == self.current_dungeon.exit_room_key:
            self.is_exit_room = True
        else:
            self.is_exit_room = False
        self.current_dungeon = self.level_map.dungeons[new_dungeon_key]
        for enemy in self.current_dungeon.enemies:
            enemy.cooldown = len(enemy.animation_database['atacar'][(1, 0)])

    def alive_check(self):
        count = 0
        for enemy in self.current_dungeon.enemies:
            if enemy.hp <= 0:
                self.current_dungeon.enemies.pop(count)
            count += 1

        if self.pj.hp <= 0:
            is_dead = True
            return is_dead


class MapRun(Run):

    def __init__(self, dung_run: DungeonRun):
        super().__init__()
        self.dungeon_screen = dung_run.draw_handler.dungeon_screen
        self.intermediate_screen = dung_run.draw_handler.intermediate_screen
        self.map_dim = dung_run.level_map.map_dim
        self.visible_rooms = dung_run.level_map.visible_rooms
        self.current_dungeon = dung_run.current_dungeon
        self.map_dict = dung_run.level_map.map_dict
        self.keyboard_handler = MapKeyboardEvents()

    def specific_run_iteration(self):
        self.draw_map(self.dungeon_screen)
        self.intermediate_screen.blit(self.dungeon_screen, (WIN_X - DUN_WIN_X - WIN_INF_BORDER_X,
                                                            WIN_Y - DUN_WIN_Y - WIN_INF_BORDER_Y))
        self.screen.blit(pygame.transform.scale(self.intermediate_screen, self.screen.get_rect().size), (0, 0))
        pygame.display.update()

    def draw_map(self, screen):
        rect_x = 10
        square_size = 16
        door_size = 5
        border_size = 1
        for x in range(self.map_dim):
            rect_y = 10
            for y in range(self.map_dim):
                name = (x, y)
                # Draw the rooms
                if name in self.visible_rooms:
                    pygame.draw.rect(screen, (200, 200, 200), pygame.Rect(rect_x + border_size, rect_y + border_size,
                                                                          square_size, square_size))
                    pygame.draw.rect(screen, (100, 100, 100), pygame.Rect(rect_x + border_size, rect_y + border_size,
                                                                          square_size, square_size), border_size)

                    if name == self.current_dungeon.key:
                        pygame.draw.rect(screen, (200, 0, 0), pygame.Rect(rect_x + border_size, rect_y + border_size,
                                                                          square_size, square_size))
                        pygame.draw.rect(screen, (100, 100, 100),
                                         pygame.Rect(rect_x + border_size, rect_y + border_size,
                                                     square_size, square_size), border_size)

                    # Draw the doors
                    for direct in self.map_dict[name]:
                        if direct == 0:
                            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(rect_x + int(square_size / 2
                                                                                           + border_size / 2),
                                                                              rect_y + square_size - int(door_size / 2)
                                                                              + border_size, border_size,
                                                                              door_size))
                        if direct == 1:
                            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(rect_x - int(door_size / 2
                                                                                           - border_size / 2) + 1,
                                                                              rect_y + int(square_size / 2)
                                                                              + border_size,
                                                                              door_size, border_size))
                        if direct == 2:
                            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(rect_x + int(square_size / 2
                                                                                           + border_size / 2),
                                                                              rect_y - int(door_size / 2) + border_size,
                                                                              border_size, door_size))
                        if direct == 3:
                            pygame.draw.rect(screen, (0, 0, 255), pygame.Rect(rect_x + square_size - int(door_size)
                                                                              + 2 * border_size + 1, rect_y
                                                                              + int(square_size / 2)
                                                                              + border_size, door_size, border_size))

                rect_y += square_size - border_size
            rect_x += square_size - border_size


class EndMenuRun(Run):

    def __init__(self, pj_dead) -> None:
        super().__init__()
        self.text = "You're dead" if pj_dead else "You won!"
        self.draw = DrawTextScreen(self, None)
        self.keyboard_handler = EndKeyboardEvents()

    def specific_run_iteration(self):
        self.draw.draw(self.screen)
        pygame.display.update()
