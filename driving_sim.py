import pygame
import random
import math
import time
import mpmath
import objects

background_colour = (255, 255, 255)
dt = 1/30

FSF = 4  # Field Scale Factor

goal_diameter = 48+4
ball_diameter = int(9.5)
goal_radius = goal_diameter*FSF/2
field_width = 324*2
field_height = 162*2
driving_speed = 15*12*FSF  # 15 ft/s

(width, height) = (field_width*FSF, field_height*FSF)

field_img = pygame.image.load(f'field_layout_{FSF}.png')


def get_center_coordinates(x, y):
    cx = int(x - width/2)
    cy = int(height/2 - y)
    theta = math.atan2(cy, cx)

    return cx, cy, theta


def get_field_coordinates(cx, cy):
    x = int(width/2 - cx)
    y = int(height/2 - cy)

    return x, y


def get_field_coordinates_polar(r, theta):
    cx = int(r * math.cos(theta))
    cy = int(r * math.sin(theta))

    return get_field_coordinates(cx, cy)


screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Tutorial 4')

particle = objects.Rectangle(
    screen, (448, 324), ball_diameter)

number_of_particles = 1
my_particles = []

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x)
             for x in range(pygame.joystick.get_count())]

joystick = pygame.joystick.Joystick(0)
joystick.init()

running = True
x = 10
y = 10
theta = 0
distances = [
    (0, 28, 90),
    (65, 28, 80),
    (140, 30, 73),
    (185, 32, 71),
    (250, 35, 70),
    (300, 35, 65),
    (400, 44, 63),
]


def interpolate_distances(d):
    try:
        for i in range(len(distances)):
            if d > distances[i][0] and d < distances[i+1][0]:
                d0 = distances[i][0]
                d1 = distances[i+1][0]
                p = (d-d0)/(d1-d0)
                v = distances[i][1] + p*(distances[i+1][1] - distances[i][1])
                theta = distances[i][2] + p * \
                    (distances[i+1][2] - distances[i][2])
                return v, theta
    except:
        return 30, 70


def get_shot_params(x, y):
    x_c, y_c, angle = get_center_coordinates(x, y)
    d = math.sqrt(x_c**2 + y_c**2)/FSF
    v, theta_v = interpolate_distances(d)
    theta_h = angle
    return v*12, theta_v*math.pi/180, math.pi - theta_h


def get_moving_shot_params(V, phi_v, phi_h, vx, vy):
    theta_h = math.atan2((V*math.cos(phi_v)*math.sin(phi_h) - vy),
                         (V*math.cos(phi_v)*math.cos(phi_h) - vx))
    theta_v = math.atan(1/((V*math.cos(phi_v)*math.cos(phi_h) -
                            vx) / (V*math.sin(phi_v)*math.cos(theta_h))))
    vs = V*math.sin(phi_v)/math.sin(theta_v)
    return vs, theta_v, theta_h


# def is_outside_field


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(background_colour)
    screen.blit(field_img, (0, 0))

    for particle in my_particles:
        particle.move()
        particle.display()
    pygame.draw.circle(screen, (0, 0, 0), (width/2, height/2),
                       goal_radius, 2*FSF)

    vx = joystick.get_axis(0)*driving_speed
    vy = joystick.get_axis(1)*driving_speed
    v_theta = joystick.get_axis(2)*5
    shoot_button = joystick.get_button(2)
    auto_aim_button = joystick.get_button(0)

    x += vx*dt
    y += vy*dt
    theta += v_theta*dt

    pygame.draw.line(screen, (0, 0, 0), (x, y), objects.get_forward_vector(
        x, y, 29*FSF, theta), 2)

    if (shoot_button == 1):
        v_shot, theta_v, theta_h = get_shot_params(x, y)
        print(v_shot, theta_v, theta_h)
        v_shot, theta_v, theta_h = get_moving_shot_params(
            v_shot, theta_v, theta_h, vx/FSF, vy/FSF)
        print(v_shot, theta_v, theta_h)
        theta = theta_h

        v_shot_x = v_shot * math.cos(theta_v) * math.cos(theta_h) * FSF
        v_shot_y = v_shot * math.cos(theta_v) * math.sin(theta_h) * FSF
        v_shot_z = v_shot * math.sin(theta_v)

        new_particle = objects.BallTrajectory(
            screen, (x, y, 0), (v_shot_x + vx, v_shot_y + vy, v_shot_z), dt)
        my_particles.append(new_particle)

    if (auto_aim_button == 1):
        # v_shot, theta_v, theta_h = get_shot_params(x, y)
        # v_shot, theta_v, theta_h = get_moving_shot_params(
        #     v_shot, theta_v, theta_h, -vx/2, -vy/2)
        # theta = theta_h
        # print(theta*180/math.pi)
        x_c, y_c, angle = get_center_coordinates(x, y)
        d = math.sqrt(x_c**2 + y_c**2)/FSF
        theta = math.pi - angle
        print(d)

    pygame.draw.polygon(screen, (0, 0, 0), objects.get_square_polygon_points(
        x, y, (29+6)*FSF, theta), 3)

    # for i in range(pygame.joystick.get_count()):
    #     joystick = pygame.joystick.Joystick(i)
    #     joystick.init()

    #     print(screen, "Joystick {}".format(i))

    #     name = joystick.get_name()
    #     print(screen, "Joystick name: {}".format(name))

    #     axes = joystick.get_numaxes()
    #     print(screen, "Number of axes: {}".format(axes))

    #     for i in range(axes):
    #         axis = joystick.get_axis(i)
    #         print(screen, "Axis {} value: {:>6.0f}".format(i, axis))

    #     buttons = joystick.get_numbuttons()
    #     print(screen, "Number of buttons: {}".format(buttons))

    #     for i in range(buttons):
    #         button = joystick.get_button(i)
    #         print(screen, "Button {:>2} value: {}".format(i, button))

    #     hats = joystick.get_numhats()
    #     print(screen, "Number of hats: {}".format(hats))

    #     for i in range(hats):
    #         hat = joystick.get_hat(i)
    #         print(screen, "Hat {} value: {}".format(i, str(hat)))

    # pygame.draw.circle(screen, (0, 0, 0), (x, y),
    #                    ball_diameter, 4)
    # particle.display()

    pygame.display.flip()
    time.sleep(dt)
