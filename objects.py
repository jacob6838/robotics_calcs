import pygame
import math

GOAL_HEIGHT = 8*12 + 8


def get_square_polygon_points(x, y, l, theta):
    points = []
    r = l/math.sqrt(2)
    for i in range(4):
        angle = theta + math.pi/2*i + math.pi/4
        points.append((int(x + r*math.cos(angle)), int(y + r*math.sin(angle))))
    points.append(points[0])
    return points


def get_forward_vector(x, y, l, theta):
    return (int(x + l*math.cos(theta)), int(y + l*math.sin(theta)))


class Object():
    def __init__(self, screen, xy, size, heading=0):
        self.x = xy[0]
        self.y = xy[1]
        self.size = size
        self.colour = (0, 0, 255)
        self.thickness = 2
        self.speed = 0
        self.angle = 0
        self.heading = 0
        self.screen = screen

    def move(self):
        self.x += math.sin(self.angle) * self.speed
        self.y -= math.cos(self.angle) * self.speed


class Rectangle(Object):
    def display(self):
        pygame.draw.polygon(self.screen, self.colour, get_square_polygon_points(
            self.x, self.y, self.size, self.heading), self.thickness)


class Circle(Object):
    def display(self):
        pygame.draw.circle(self.screen, self.colour, (int(
            self.x), int(self.y)), self.size, self.thickness)


class BallTrajectory():
    def __init__(self, screen, xyz, vxyz, dt, FSF=2):
        self.x = xyz[0]
        self.y = xyz[1]
        self.z = xyz[2]
        self.vx = vxyz[0]
        self.vy = vxyz[1]
        self.vz = vxyz[2]
        self.colour = (0, 0, 255)
        self.thickness = 2*FSF
        self.screen = screen
        self.did_reach_height = False
        self.dt = dt
        self.FSF = FSF

    def move(self):
        self.x += self.vx * self.dt
        self.y += self.vy * self.dt
        self.z += self.vz * self.dt
        self.vz -= 32.17*12 * self.dt
        if self.did_reach_height:
            if self.z <= GOAL_HEIGHT:  # hit goal height, stop ball and set size
                self.vx = 0
                self.vy = 0
                self.vz = 0
                self.size = 2*self.FSF
            else:  # above goal, not low enough yet
                self.size = int(self.z/12)*self.FSF
        elif self.z >= GOAL_HEIGHT:
            self.did_reach_height = True
            self.size = int(self.z/12)*self.FSF
        elif self.z < 0:  # below ground
            self.vx = 0
            self.vy = 0
            self.vz = 0
            self.size = 2*self.FSF
        else:
            self.size = int(self.z/12)*self.FSF

    def display(self):
        pygame.draw.circle(self.screen, self.colour, (int(
            self.x), int(self.y)), self.size, self.thickness)
