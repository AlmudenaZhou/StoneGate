# from dataclasses import dataclass, field
#
# from pyrsistent import s
#
# from scripts.menus.text import Text
from scripts.menus.get_modules import GetFunction

import pygame


class Menu:

    def __init__(self, position, size) -> None:
        
        self.position = position
        self.size = size
        self.selected_button: Button
        self.button_list: list[Button]

        button_data = self.get_button_data()
        self.generate_buttons(button_data=button_data)

        self.menu_active: bool = True

    def start(self, button_data: list = None):
        if button_data:
            self.update_buttons(button_data)

    def main(self, event) -> dict:
        if event.type == pygame.KEYDOWN:
            button_answer = self.key_action(event)

            if button_answer['menu_active'] in button_answer:
                self.menu_active = button_answer['menu_active']
                return None

        return button_answer

    @staticmethod
    def end():
        return False

    def generate_buttons(self, button_data):
        MenuClass = GetFunction.import_menus_class()

        for data in button_data:
            data['action']: function = GetFunction.get_function(MenuClass, data['action'])
            button = Button(Button.autoincrement_id(self.button_list), data['position'], data['scree_position'],
                            data['enabled'], data['action'], data['display'], data["params"])

            self.button_list.append(button)

    def key_action(self, keys):
        
        button_answer: dict = None
        movement_direction = None

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            movement_direction = (0, -1)

        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            movement_direction = (0, 1)

        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            movement_direction = (-1, 0)

        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            movement_direction = (1, 0)

        elif keys[pygame.K_KP_ENTER]:
            button_answer = self.selected_button.action()
        
        elif keys[pygame.K_ESCAPE]:
            button_answer = dict()
            button_answer['menu_active'] = self.end()

        if movement_direction:
            self.change_selected_button(movement_direction)

        return button_answer

    def change_selected_button(self, movement_direction):
        actual_postion = self.selected_button.position
        last_button_distance = (100, 100)

        for button in self.button_list:
            if not button.enabled:
                continue

            new_distance = (actual_postion - button.position) * movement_direction
            if new_distance <= last_button_distance and new_distance >= (1, 1):
                last_button = button
                last_button_distance = new_distance

        if last_button != (100, 100):
            self.selected_button = last_button

    def get_button_data(self):
        button_data: list[dict] = list()

        return button_data

    def update_buttons(self, button_data):
        for data in button_data:
            for button in self.button_list:
                if button.id_ == data['button_id']:
                    button.params = data['button_params']


class Button:

    def __init__(self, id_, position, screen_position, size, enabled, action, display, params) -> None:
        self.id_: int = id_
        self.position: list[int, int] = position
        self.screen_position: list[int, int] = screen_position
        self.size: list[int, int] = size
        self.enabled: bool = enabled
        self.action: function = action
        self.display: str = display
        self.params: dict = params
    

    @staticmethod
    def autoincrement_id(button_list):
        max_id = 0
        if not len(button_list):
            return max_id

        max_id = button_list[-1].id_
        return max_id + 1

class ButtonStandar(Button):

    def get_image(self):
        image_name = self.display
        return image_name

class ButtonText(Button):
    
    def __init__(self, id_, position, screen_position, size, enabled, action, display, params) -> None:
        super().__init__(id_, position, screen_position, size, enabled, action, display, params)
        self.active: bool = False
        self.action = self.display.textEdit

