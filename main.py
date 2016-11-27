import asyncio
import math
import threading

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory


class WebSocketServer(WebSocketServerProtocol):
    def onConnect(self, request):
        print("Connection from: " + request.peer)

    def onOpen(self):
        print("Connection open")

    def onMessage(self, payload, isBinary):
        data = payload.decode('utf8')

        try:
            data = int(data)
        except ValueError:
            """"""

        if data == 0:
            """"""
        elif data == 1:
            Main.player.pos[0] += 1
        elif data == 2:
            Main.player.pos[2] -= 1
        elif data == 3:
            Main.player.pos[2] += 1
        elif data == 4:
            Main.player.pos[0] -= 1

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


def web_socket_server():
    loop = asyncio.new_event_loop()

    asyncio.set_event_loop(loop)

    factory = WebSocketServerFactory(u"ws://127.0.0.1:8081")
    factory.protocol = WebSocketServer

    loop.run_until_complete(loop.create_server(factory, '0.0.0.0', 8081))
    loop.run_forever()


threading.Thread(target=web_socket_server).start()


class Camera:
    # position of the camera - x, y, z
    pos = [0, 1, 0]
    # rotation of the camera - x, y, z
    rot = [0, 0, 0]

    def look(self):
        dx, dy = pygame.mouse.get_rel()

        # look sensitivity - lower is faster, higher is slower
        sensitivity = 10

        self.rot[0] -= dy / sensitivity
        self.rot[1] -= dx / sensitivity

    def move(self):
        yaw = math.radians(-self.rot[1])

        # camera velocity - lower is faster, higher is slower
        velocity = 20

        dx = math.sin(yaw) / velocity
        dz = math.cos(yaw) / velocity

        keys = pygame.key.get_pressed()

        # handle movement
        if keys[pygame.K_w]:
            self.pos[0] += dx
            self.pos[2] -= dz
        if keys[pygame.K_s]:
            self.pos[0] -= dx
            self.pos[2] += dz
        if keys[pygame.K_a]:
            self.pos[0] -= dz
            self.pos[2] -= dx
        if keys[pygame.K_d]:
            self.pos[0] += dz
            self.pos[2] += dx


class Main:
    # screen resolution & aspect ratio
    width = 1200
    height = 720
    aspect_ratio = width / height

    # field of view
    fov = 65

    # player is a Camera object
    player = Camera()
    mouse_lock = True

    # size of the terrain
    terrain_width = 10
    terrain_depth = 10

    # boundaries along x and z axis
    left = -terrain_width / 2
    right = terrain_width / 2
    front = terrain_depth / 2
    back = -terrain_depth / 2

    # terrain vertices
    terrain = ((left, 0, front), (left, 0, back), (right, 0, back), (right, 0, front))

    # game state variable
    game_running = True

    def __init__(self):
        pygame.init()
        pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF | pygame.OPENGL)
        pygame.display.set_caption("FPyS")

        # 'sky box' colour
        glClearColor(0.5, 0.7, 1, 1.0)

        while self.game_running:
            self.game_loop()

    def game_loop(self):
        # setup opengl
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # set fov, aspect ratio, near clipping, far clipping
        gluPerspective(self.fov, self.aspect_ratio, 0.1, 20)

        # lock the mouse to the view
        if self.mouse_lock:
            pygame.mouse.set_visible(False)
            pygame.event.set_grab(1)
        else:
            pygame.mouse.set_visible(True)
            pygame.event.set_grab(0)

        # handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.mouse_lock = False
                    self.game_running = False

        # update player
        self.player.move()
        self.player.look()

        glPushMatrix()

        # move and rotate player
        pos = self.player.pos
        rot = self.player.rot
        glRotatef(-rot[2], 0, 0, 1)
        glRotatef(-rot[0], 1, 0, 0)
        glRotatef(-rot[1], 0, 1, 0)
        glTranslate(-pos[0], -pos[1], -pos[2])

        # draw terrain
        glBegin(GL_QUADS)
        for vertex in self.terrain:
            glColor3fv((0, 0.25, 0))
            glVertex3fv(vertex)
        glEnd()

        # draw walls
        glBegin(GL_QUADS)
        # left
        glColor3fv((1, 0.2, 0.2))
        glVertex3fv((self.left, 0, self.front))
        glVertex3fv((self.left, 0, self.back))
        glVertex3fv((self.left, 1, self.back))
        glVertex3fv((self.left, 1, self.front))

        # right
        glColor3fv((1, 1, 0.2))
        glVertex3fv((self.right, 0, self.front))
        glVertex3fv((self.right, 0, self.back))
        glVertex3fv((self.right, 1, self.back))
        glVertex3fv((self.right, 1, self.front))

        # front
        glColor3fv((1, 0.2, 0.2))
        glVertex3fv((self.front, 0, self.left))
        glVertex3fv((self.back, 0, self.left))
        glVertex3fv((self.back, 1, self.left))
        glVertex3fv((self.front, 1, self.left))

        # back
        glColor3fv((1, 1, 0.2))
        glVertex3fv((self.front, 0, self.right))
        glVertex3fv((self.back, 0, self.right))
        glVertex3fv((self.back, 1, self.right))
        glVertex3fv((self.front, 1, self.right))
        glEnd()

        glPopMatrix()

        # update display
        pygame.display.flip()
        pygame.time.Clock().tick(60)


Main()
quit()
