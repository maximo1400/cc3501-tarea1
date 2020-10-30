"""
Clase controlador, obtiene el input, lo procesa, y manda los mensajes
a los modelos.
"""

from modelos import SnakeLogic, Apple
import glfw
import sys
from typing import Union


class Controller(object):
    model: Union['SnakeLogic', None]
    apple: Union['Apple', None]

    def __init__(self):
        self.model = None
        self.apple = None
        self.fillPolygon = True

    def set_model(self, m):
        self.model = m

    def set_apple(self, e):
        self.apple = e

    def on_key(self, window, key, scancode, action, mods):
        if not (action == glfw.PRESS or action == glfw.RELEASE):
            return

        if key == glfw.KEY_ESCAPE:
            sys.exit()

        # Controlador modifica al modelo
        elif (key == glfw.KEY_LEFT or key == glfw.KEY_A) and action == glfw.PRESS:
            # print('Turn left')
            self.model.turn_left()

        elif (key == glfw.KEY_RIGHT or key == glfw.KEY_D) and action == glfw.PRESS:
            # print('Turn right')
            self.model.turn_right()

        elif (key == glfw.KEY_UP or key == glfw.KEY_W) and action == glfw.PRESS:
            # print('Turn up')
            self.model.turn_up()

        elif (key == glfw.KEY_DOWN or key == glfw.KEY_S) and action == glfw.PRESS:
            # print('Turn down')
            self.model.turn_down()

        # Raton toca la pantalla....
        # else:
            # print('Unknown key')
