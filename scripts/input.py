import sys
import time

import pygame

from .utils import read_json, write_json

class InputState:
    def __init__(self):
        self.pressed = False
        self.just_pressed = False
        self.just_released = False
        self.held_since = 0

    def update(self):
        self.just_pressed = False
        self.just_released = False

    def press(self):
        self.pressed = True
        self.just_pressed = True
        self.held_since = time.time()

    def unpress(self):
        self.pressed = False
        self.just_released = True

class Mouse:
    def __init__(self, game):
        self.game = game
        self.pos = (0, 0)
        self.ui_pos = (0, 0)

    def update(self):
        x, y = pygame.mouse.get_pos()
        self.pos = (int(x / self.game.window.scaled_resolution[0] * self.game.window.base_resolution[0]), int(y / self.game.window.scaled_resolution[1] * self.game.window.base_resolution[1]))
        self.ui_pos = (x, y)

class Input:
    def __init__(self, game):
        self.game = game
        self.state = 'main'
        self.text_buffer = None

        self.path = 'data/config/input.json'
        self.load_config(self.path)
        self.hidden_keys = ['__backspace']
        
        self.repeat_rate = 0.02
        self.repeat_delay = 0.5
        self.repeat_times = {key: time.time() for key in self.config}
        self.valid_chars = [' ', '.', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ',', ';', '-', '=', '/', '\\', '[', ']', '\'']
        self.shift_mappings = {
            '1': '!',
            '8': '*',
            '9': '(',
            '0': ')',
            ';': ':',
            ',': '<',
            '.': '>',
            '/': '?',
            '\'': '"',
            '-': '_',
            '=': '+',
        }
        self.shift = False
        
        self.mouse = Mouse(game)

        self.controllers = None

        self.binding_listen = None

    def save_config(self):
        write_json(self.path, {binding: self.config[binding] for binding in self.config if binding not in self.hidden_keys})

    def load_config(self, path):
        self.config = read_json(path)
        self.config['__backspace'] = ['keyboard', pygame.K_BACKSPACE]
        self.input = {key : InputState() for key in self.config}

    def binding_listen_callback(self, func):
        self.binding_listen = func

    def pressed(self, key):
        return self.input[key].just_pressed if key in self.input else False
    
    def consume(self, key):
        self.input[key].just_pressed = False
        self.input[key].pressed = False

    def holding(self, key):
        return self.input[key].pressed if key in self.input else False

    def released(self, key):
        return self.input[key].just_released if key in self.input else False

    def movement(self):
        pass
    
    def set_text_buffer(self, text_buffer=None):
        self.text_buffer = text_buffer

    def update(self):
        for state in self.input.values():
            state.update()

        self.mouse.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == 27):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.binding_listen:
                    self.binding_listen(['mouse', event.button])
                    self.binding_listen = None
                else:
                    for mapping in self.config:
                        if self.config[mapping][0] == 'mouse':
                            if event.button == self.config[mapping][1]:
                                self.input[mapping].press()
            if event.type == pygame.MOUSEBUTTONUP:
                for mapping in self.config:
                    if self.config[mapping][0] == 'mouse':
                        if event.button == self.config[mapping][1]:
                            self.input[mapping].unpress()
            if event.type == pygame.KEYDOWN:
                if self.binding_listen:
                    self.binding_listen(['keyboard', event.key])
                    self.binding_listen = None
                else:
                    if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                        self.shift = True
                            
                    if self.text_buffer:
                        for char in self.valid_chars:
                            new_char = None
                            if event.key == ord(char):
                                new_char = char
                            if new_char:
                                if self.shift:
                                    new_char = new_char.upper()
                                    if new_char in self.shift_mappings:
                                        new_char = self.shift_mappings[new_char]
                                self.text_buffer.insert(new_char)
                        
                        if event.key == pygame.K_RETURN:
                            self.text_buffer.enter()
                                
                    mappings = self.config
                    if self.text_buffer:
                        mappings = self.hidden_keys
                        
                    for mapping in mappings:
                        if self.config[mapping][0] == 'keyboard':
                            if event.key == self.config[mapping][1]:
                                self.input[mapping].press()
                                
            if event.type == pygame.KEYUP:
                for mapping in self.config:
                    if self.config[mapping][0] == 'keyboard':
                        if event.key == self.config[mapping][1]:
                            self.input[mapping].unpress()
                
                if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                    self.shift = False
        
        if self.text_buffer:
            if self.pressed('__backspace'):
                self.repeat_times['__backspace'] = self.game.window.time
                self.text_buffer.delete()
            
            if self.holding('__backspace'):
                while self.game.window.time > self.repeat_times['__backspace'] + self.repeat_delay + self.repeat_rate:
                    self.repeat_times['__backspace'] += self.repeat_rate
                    self.text_buffer.delete()
