import transformations as tr
import basic_shapes as bs
import scene_graph as sg
import easy_shaders as es
import numpy as np

from OpenGL.GL import *
import random

# direcciones
RIGHT = 0
UP = 1
LEFT = 2
DOWN = 3


class Map(object):
    def __init__(self, size=10):
        gpu_table_quad = es.toGPUShape(bs.createColorQuad(0.1, 0.8, 0.1))
        gpu_border_quad = es.toGPUShape(bs.createColorQuad(1, 0, 0))

        table = sg.SceneGraphNode('table')
        table.transform = tr.uniformScale((size + 1) / (size + 2))
        table.childs += [gpu_table_quad]

        border = sg.SceneGraphNode('border')
        border.transform = tr.uniformScale(1)
        border.childs += [gpu_border_quad]

        game_map = sg.SceneGraphNode('map')
        game_map.transform = tr.matmul([tr.uniformScale(2)])
        game_map.childs += [border, table]

        transform_map = sg.SceneGraphNode('mapTR')
        transform_map.childs += [game_map]

        self.model = transform_map

        self.size = size + 2

    def inside_borders(self, snake):
        x, y = snake.pos[0]
        if 0 < x < self.size - 1 and 0 < y < self.size - 1:
            return True
        print(f"Pared en ({x, y})")
        return False

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        sg.drawSceneGraphNode(self.model, pipeline, 'transform')


class SnakeLogic(object):

    def __init__(self, size):
        middle = int(size / 2)
        self.map_size = size
        self.pos = [(middle, middle), (middle, middle + 1), (middle, middle + 2)]
        self.dir = LEFT
        self.is_alive = True
        self.needs_extending = False

    def turn_left(self):
        if self.dir != RIGHT:
            self.dir = LEFT

    def turn_right(self):
        if self.dir != LEFT:
            self.dir = RIGHT

    def turn_up(self):
        if self.dir != DOWN:
            self.dir = UP

    def turn_down(self):
        if self.dir != UP:
            self.dir = DOWN

    def move(self):
        x, y = self.pos[0]
        if self.dir == LEFT:
            if self.pos[1] == (x - 1, y):  # Evita el suicidio por giros de 180°
                # print("Mucho giro, Move Right")
                self.pos.insert(0, (x + 1, y))
            else:
                # print("Move Left")
                self.pos.insert(0, (x - 1, y))

        if self.dir == RIGHT:
            if self.pos[1] == (x + 1, y):
                # print("Mucho giro, Move Left")
                self.pos.insert(0, (x - 1, y))
            else:
                # print("Move Right")
                self.pos.insert(0, (x + 1, y))

        if self.dir == UP:
            if self.pos[1] == (x, y + 1):
                # print("Mucho giro, Move Down")
                self.pos.insert(0, (x, y - 1))
            else:
                # print("Move Up")
                self.pos.insert(0, (x, y + 1))

        if self.dir == DOWN:
            if self.pos[1] == (x, y - 1):
                # print("Mucho giro, Move Up")
                self.pos.insert(0, (x, y + 1))
            else:
                # print("Move Down")
                self.pos.insert(0, (x, y - 1))

        if not self.needs_extending:  # Extencion del cuerpo
            self.pos.pop()

        self.needs_extending = False

    def collide(self, apple, the_map):
        x, y = self.pos[0]
        if self.pos[0] in self.pos[1:]:
            print("suicidacion")
            self.is_alive = False
        if not the_map.inside_borders(self):
            print("chocacion")
            self.is_alive = False
        if apple.pos_x == x and apple.pos_y == y:
            print("comidacion")
            self.needs_extending = True
            apple.re_position()


class SnakeMaker(object):
    def __init__(self, snake_logic):
        # Figuras básicas
        gpu_head_quad = es.toGPUShape(bs.createTextureQuad("img/robot.png"), GL_REPEAT,
                                      GL_NEAREST)  # GL_CLAMP_TO_BORDER
        gpu_body_quad = es.toGPUShape(bs.createTextureQuad("img/body.png"), GL_REPEAT, GL_NEAREST)

        # gpu_head_quad = es.toGPUShape(bs.createColorQuad(0, 0, 1))
        # gpu_body_quad = es.toGPUShape(bs.createColorQuad(1, 0, 1))

        head = sg.SceneGraphNode('head')
        x, y = snake_logic.pos[0]
        head.transform = tr.translate(x - snake_logic.map_size / 2, y - snake_logic.map_size / 2, 0)
        head.childs += [gpu_head_quad]

        # Cuerpo generico
        body = sg.SceneGraphNode('body')
        body.transform = tr.uniformScale(1)
        body.childs += [gpu_body_quad]

        snake = sg.SceneGraphNode('snake')
        snake.transform = tr.uniformScale(2 / (snake_logic.map_size + 2))
        snake.childs += [head]

        x_old, y_old = snake_logic.pos[1]
        snake_len = len(snake_logic.pos)
        body_parts = []
        for bit in range(1, snake_len):
            body_parts.append(sg.SceneGraphNode(f'bodyPart{bit}'))
            x, y = snake_logic.pos[bit]
            body_parts[bit - 1].transform = tr.translate(x - snake_logic.map_size / 2, y - snake_logic.map_size / 2, 0)
            body_parts[bit - 1].childs += [body]
            snake.childs += [body_parts[bit - 1]]
        # Ensamblamos el snek

        transform_snake = sg.SceneGraphNode('snakeTR')
        transform_snake.childs += [snake]

        self.model = transform_snake

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.identity())
        sg.drawSceneGraphNode(sg.findNode(self.model, 'snake'), pipeline, "transform")

        # glUniformMatrix4fv(glGetUniformLocation(pipeline.shaderProgram, "transform"), 1, GL_TRUE, tr.identity())
        # sg.drawSceneGraphNode(self.model, pipeline, 'transform')


class Apple(object):

    def __init__(self, size):
        self.map_size = size
        self.pos_y = 0
        self.pos_x = 0
        self.re_position()

        gpu_apple = es.toGPUShape(bs.createColorQuad(0, 0, 0))

        apple = sg.SceneGraphNode('apple')
        apple.transform = tr.uniformScale(1)
        apple.childs += [gpu_apple]

        apple_tr = sg.SceneGraphNode('appleTR')
        apple_tr.childs += [apple]
        self.model = apple_tr

    def draw(self, pipeline):
        glUseProgram(pipeline.shaderProgram)
        self.model.transform = tr.matmul([tr.uniformScale(2 / (self.map_size + 2)),
                                          tr.translate(self.pos_x - self.map_size / 2, self.pos_y - self.map_size / 2,
                                                       0)])
        sg.drawSceneGraphNode(self.model, pipeline, "transform")

    def re_position(self):
        self.pos_x = random.randint(1, self.map_size)
        self.pos_y = random.randint(1, self.map_size)
        print(f"New apple:({self.pos_x, self.pos_y})")
