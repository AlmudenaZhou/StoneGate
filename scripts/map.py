import json
import random
import os
from abc import abstractmethod

from scripts.entity.enemies import Moco, Tostada, Conejo, Boca, Boss

from scripts.objects import Doors
from scripts.variables import general_path, DUN_WIN_X, DUN_WIN_Y


class Map:

    def __init__(self, save_data, dungeon_element):
        # map dimension by level
        self.map_data = self.read_map_data()
        # player game information (level, objects, ...)
        self.level = save_data['floor']
        self.map_dim = self.map_data['lvl' + str(self.level)]
        # Minimum number of rooms required to finish the dungeon
        self.room_to_the_exit = self.map_dim + random.randint(1, int(self.map_dim**2 / 5 + 1))
        # dict with the rooms and its DungeonMap object associate | (x, y): DungeonMap
        self.dungeons = {}
        # dict with the rooms and its activated doors | (x, y): active doors list
        self.map_dict = {}
        # initial room | (x, y)
        self.entry_room_key = ()
        # set with the visible room keys
        self.visible_rooms = set()
        # exit_room key room
        self.exit_room_key = None
        self.room_mapper = eval(dungeon_element.capitalize() + str('Mapper'))
        self.dungeon_element = dungeon_element

    @staticmethod
    def read_map_data():
        with open(os.path.join(general_path, 'configurations', 'map_parameters.txt'), 'r') as outfile:
            map_data = json.load(outfile)
        return map_data

    # --------------------------------------- Map Generation --------------------------------------- #
    def starting_point(self):
        """
        Gets one of the four edges that compound the map. It starts in the middle of each edge, following the
        directions: 0: down, 1: left, 2: up, 3: right
        """
        start_point = random.randint(0, 3)
        if start_point == 0:
            start_x = int((self.map_dim - 1) / 2)
            start_y = self.map_dim - 1
        elif start_point == 1:
            start_x = 0
            start_y = int((self.map_dim - 1) / 2)
        elif start_point == 2:
            start_x = int((self.map_dim - 1) / 2)
            start_y = 0
        elif start_point == 3:
            start_x = self.map_dim - 1
            start_y = int((self.map_dim - 1) / 2)
        else:
            raise ValueError('start_point must be between 0 and 3 both included')
        self.entry_room_key = (start_x, start_y)

    def list_possible_dir(self, x, y):
        """
        Returns a list with the possible directions in a specific room (x, y) considering the previous rooms in the map.
        :param x:
        :param y:
        :return:
        """
        possible_ways = []
        for new_x in range(max(x - 1, 0), min(x + 2, self.map_dim)):
            if (new_x, y) not in self.map_dict.keys():
                if x < new_x:
                    possible_ways.append(3)
                elif x > new_x:
                    possible_ways.append(1)
        for new_y in range(max(y - 1, 0), min(y + 2, self.map_dim)):
            if (x, new_y) not in self.map_dict.keys():
                if y > new_y:
                    possible_ways.append(2)
                elif y < new_y:
                    possible_ways.append(0)
        return possible_ways

    def generate_level_map(self):
        """
        Generates map_dict. (x, y): list of active doors. It starts with the starting_point and choose randomly
        n directions from list_possible_dir for each room through the room_loop function until room_to_the_exit rooms
        are reached . If the condition cannot be satisfied (n_it >= 10), it restarts the map generation in
        order to find a solution.
        The doors follows 0: down, 1: left, 2: up, 3: right
        :return:
        """
        self.visible_rooms = set()
        self.starting_point()
        map_dict = {self.entry_room_key: []}
        self.visible_rooms.add(self.entry_room_key)
        self.map_dict = map_dict
        current_room = self.entry_room_key
        unexplored_rooms = self.choose_the_doors(current_room)
        n_rooms = 1
        n_it = 0
        while self.room_to_the_exit > n_rooms:
            future_unexplored_rooms = self.room_loop(unexplored_rooms)
            if abs(n_rooms - self.room_to_the_exit) > 0:
                n_it = 0
                while len(future_unexplored_rooms) <= random.randint(0, 1):
                    future_unexplored_rooms = self.room_loop(unexplored_rooms)
                    if n_it > 10:
                        break
                    n_it += 1
            if n_it > 10:
                break

            if abs(n_rooms - self.room_to_the_exit) == 1 or len(future_unexplored_rooms) == 0:
                exit_room = random.choice(future_unexplored_rooms)
                self.exit_room_key = exit_room
                break
            unexplored_rooms = future_unexplored_rooms
            n_rooms += 1

        if n_it > 10:
            self.generate_level_map()

        self.dic_dungeons()

    def room_loop(self, unexplored_rooms):
        """
        Loop to get the possible future rooms for one specific room, considering the possible doors.
        :param unexplored_rooms:
        :return:
        """
        future_unexplored_rooms = []
        for room in unexplored_rooms:
            current_room = room
            future_unexplored_rooms += self.choose_the_doors(current_room)
        return future_unexplored_rooms

    def choose_the_doors(self, current_room):
        """
        Chooses the doors for a specific room and tracks them in the dictionary for both the actual and the future room.
        The doors follows 0: down, 1: left, 2: up, 3: right
        :param current_room:
        :return:
        """
        possible_doors = self.list_possible_dir(current_room[0], current_room[1])
        current_room_name = (current_room[0], current_room[1])
        if len(possible_doors) >= 1:
            n_doors = random.randint(0, len(possible_doors))
            if n_doors > len(possible_doors):
                n_doors = len(possible_doors)
            doors = random.sample(possible_doors, n_doors)
            rooms = []
            for door in doors:
                if door == 0:
                    new_room_name = (current_room[0], current_room[1] + 1)
                    rooms.append(new_room_name)
                    self.map_dict[current_room_name].append(0)
                    self.map_dict[new_room_name] = [2]
                elif door == 1:
                    new_room_name = (current_room[0] - 1, current_room[1])
                    rooms.append(new_room_name)
                    self.map_dict[current_room_name].append(1)
                    self.map_dict[new_room_name] = [3]
                elif door == 2:
                    new_room_name = (current_room[0], current_room[1] - 1)
                    rooms.append(new_room_name)
                    self.map_dict[current_room_name].append(2)
                    self.map_dict[new_room_name] = [0]
                elif door == 3:
                    new_room_name = (current_room[0] + 1, current_room[1])
                    rooms.append(new_room_name)
                    self.map_dict[current_room_name].append(3)
                    self.map_dict[new_room_name] = [1]
        else:
            rooms = []

        return rooms

    def dic_dungeons(self):

        for dungeon in self.map_dict.keys():
            self.dungeons[dungeon] = self.room_mapper(dungeon, self.create_dungeons_doors(dungeon), self.entry_room_key,
                                                      self.exit_room_key, self.dungeon_element)

    def create_dungeons_doors(self, dungeon):
        """
        return a list of 4 bools True if the door exists and False if not.
        If the door exists, then it must be in the list for this dungeon key in map_dict.
        :param dungeon:
        :return:
        """
        doors_handler = Doors(self.dungeon_element)
        doors_handler.create_doors(DUN_WIN_X, DUN_WIN_Y)
        for index, door in enumerate(doors_handler.doors):
            if index in self.map_dict[dungeon]:
                door.exist = True
            else:
                door.exist = False
        return doors_handler


class RoomMapper:

    def __init__(self, directory, doors_handler, entry_room_key, exit_room_key, dungeon_element):
        self.key = directory
        # List of four booleans. The door index follows 0: down, 1: left, 2: up, 3: right.
        self.doors_handler = doors_handler
        self.exit_room_key = exit_room_key
        self.entry_room_key = entry_room_key
        self.dungeon_element = dungeon_element
        self.room = self.map_room()
        self.enemies = self.room['enemies']
        self.objects = self.room['objects']

    def map_room(self):
        if self.exit_room_key == self.key:
            room = self.generate_exit_room()
        elif self.entry_room_key == self.key:
            room = self.create_empty_room()
        else:
            room = self.generate_general_room()
        return room

    @staticmethod
    def create_empty_room():
        return {'enemies': [], 'objects': []}

    @abstractmethod
    def generate_exit_room(self):
        pass

    def generate_general_room(self):
        room_method_list = [method for method in dir(self) if method.startswith('room')]
        room = self.create_empty_room()
        if len(room_method_list):
            room_method = getattr(self, random.choice(room_method_list))
            room = room_method()
        return room


class TutorialMapper(RoomMapper):

    def generate_exit_room(self):
        enemy1 = Boss(pos_x=60, pos_y=20, element='light')
        room = self.create_empty_room()

        room['enemies'].extend([enemy1])
        return room

    def room1(self):
        enemy1 = Tostada(pos_x=60, pos_y=20, element='water')

        enemy2 = Moco(pos_x=200, pos_y=90, element='fire')

        room = self.create_empty_room()

        room['enemies'].extend([enemy1, enemy2])

        return room

    def room2(self):
        enemy1 = Conejo(pos_x=200, pos_y=90, element='water')

        enemy2 = Moco(pos_x=90, pos_y=90, element='darkness')

        room = self.create_empty_room()

        room['enemies'].extend([enemy1, enemy2])

        return room

    def room3(self):
        enemy1 = Boca(pos_x=30, pos_y=30, element='light')

        enemy2 = Conejo(pos_x=200, pos_y=200, element='water')

        room = self.create_empty_room()

        room['enemies'].extend([enemy1, enemy2])

        return room

    def room4(self):
        enemy1 = Moco(pos_x=150, pos_y=150, element='air')

        enemy2 = Conejo(pos_x=200, pos_y=200, element='darkness')

        room = self.create_empty_room()

        room['enemies'].extend([enemy1, enemy2])

        return room

    def room5(self):
        enemy1 = Conejo(pos_x=30, pos_y=30, element='light')
        enemy2 = Boca(pos_x=30, pos_y=200)
        enemy3 = Tostada(pos_x=150, pos_y=150)

        room = self.create_empty_room()

        room['enemies'].extend([enemy1, enemy2, enemy3])

        return room
