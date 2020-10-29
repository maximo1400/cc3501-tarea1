"""
Esta sería la clase vista. Contiene el ciclo de la aplicación y ensambla
las llamadas para obtener el dibujo de la escena.
"""
import time
import glfw
from OpenGL.GL import *
import sys

from modelos import *
from controller import Controller

if __name__ == '__main__':

    # Initialize glfw
    if not glfw.init():
        sys.exit()

    width = 800
    height = 800

    window = glfw.create_window(width, height, 'Robo Snek', None, None)

    if not window:
        glfw.terminate()
        sys.exit()

    glfw.make_context_current(window)

    controlador = Controller()

    # Connecting the callback function 'on_key' to handle keyboard events
    glfw.set_key_callback(window, controlador.on_key)

    # Assembling the shader program (pipeline) with both shaders
    pipeline_color = es.SimpleTransformShaderProgram()
    pipeline_texture = es.SimpleTextureTransformShaderProgram()

    # Telling OpenGL to use our shader program
    glUseProgram(pipeline_color.shaderProgram)

    # Setting up the clear screen color
    glClearColor(0.85, 0.85, 0.85, 1.0)

    # Enabling transparencies
    glEnable(GL_BLEND)
    # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # HACEMOS LOS OBJETOS
    size_input = int(sys.argv[1])
    if size_input < 10 or size_input > 50:
        size_input = 10

    game_map = Map(size_input)
    snake = SnakeLogic(size_input)
    apple = Apple(size_input)

    controlador.set_model(snake)
    controlador.set_apple(apple)

    t0 = 0

    while snake.is_alive and not glfw.window_should_close(window):  # Dibujando --> 1. obtener el input

        # Calculamos el dt
        ti = glfw.get_time()
        dt = ti - t0

        time.sleep(np.abs(0.2 - dt))
        t0 = ti

        # Using GLFW to check for input events
        glfw.poll_events()  # OBTIENE EL INPUT --> CONTROLADOR --> MODELOS

        # Clearing the screen in both, color and depth
        glClear(GL_COLOR_BUFFER_BIT)

        # Reconocer la logica
        snake.move()
        snake.collide(apple, game_map)
        snake_drawing = SnakeMaker(snake)

        # DIBUJAR LOS MODELOS
        game_map.draw(pipeline_color)
        SnakeMaker(snake).draw(pipeline_texture)
        # pipeline_color.drawShape(snake_drawing.model)
        apple.draw(pipeline_color)

        # Once the render is done, buffers are swapped, showing only the complete scene.
        glfw.swap_buffers(window)

    print("muricion")
    glfw.terminate()
