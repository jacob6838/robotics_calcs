import pygame
import random
import math
import time
import mpmath
import objects

background_colour = (255, 255, 255)
dt = 1/30

FSF = 2  # Field Scale Factor

goal_diameter = 48
ball_diameter = int(9.5)
goal_radius = goal_diameter*FSF/2
field_width = 324*2
field_height = 162*2
driving_speed = 15*12*FSF  # 15 ft/s

(width, height) = (field_width*FSF, field_height*FSF)


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
print(get_field_coordinates_polar(200, 0))

number_of_particles = 1
my_particles = []

# for n in range(number_of_particles):
#     size = random.randint(50, 100)
#     x = random.randint(size, width-size)
#     y = random.randint(size, height-size)

#     particle = objects.Rectangle(screen, (x, y), size)
#     particle.speed = random.random()
#     particle.angle = random.uniform(0, math.pi*2)

#     my_particles.append(particle)

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x)
             for x in range(pygame.joystick.get_count())]
# joystick = pygame.joystick.Joystick(0)
print(screen, "Number of joysticks: {}".format(pygame.joystick.get_count()))

# sample_surface = pygame.Surface((400, 300), pygame.SRCALPHA)
# sample_surface.fill(0, 0, 0)

joystick = pygame.joystick.Joystick(0)
joystick.init()

running = True
x = 10
y = 10
theta = 0
distances = [
    (0, 25, 90),
    (65, 25, 80),
    (140, 30, 75),
    (185, 30, 70),
    (250, 35, 70),
    (300, 38, 70),
    (100000, 38, 70),
]


def interpolate_distances(d):
    try:
        for i in range(len(distances)):
            if d > distances[i][0] and d < distances[i+1][0]:
                d0 = distances[i][0]
                d1 = distances[i+1][0]
                p = (d-d0)/(d1-d0)
                print(d0, d, d1, p)
                v = distances[i][1] + p*(distances[i+1][1] - distances[i][1])
                theta = distances[i][2] + p * \
                    (distances[i+1][2] - distances[i][2])
                return v, theta
    except:
        return 30, 70


def get_shot_params(x, y):
    x_c, y_c, angle = get_center_coordinates(x, y)
    d = math.sqrt(x_c**2 + y_c**2)/2
    v, theta_v = interpolate_distances(d)
    theta_h = angle
    return v*12, theta_v*math.pi/180, math.pi - theta_h


def get_moving_shot_params(V, phi_v, phi_h, vx, vy):
    theta_h = math.atan((V*math.cos(phi_v)*math.sin(phi_h) + vy) /
                        (V*math.cos(phi_v)*math.cos(phi_h) + vx))
    theta_v = mpmath.acot((V*math.cos(phi_v)*math.cos(phi_h) +
                          vx) / (V*math.sin(phi_v)*math.cos(theta_h)))
    vs = V*math.sin(phi_v)/math.sin(theta_v)
    return vs, theta_v, theta_h


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill(background_colour)

    for particle in my_particles:
        particle.move()
        particle.display()
    pygame.draw.circle(screen, (0, 0, 0), (width/2, height/2),
                       goal_diameter*FSF/2, 2*FSF)

    # (x, y) = get_field_coordinates_polar(200, math.pi*i/dt)
    # particle.x = x
    # particle.y = y

    vx = joystick.get_axis(0)*driving_speed
    vy = joystick.get_axis(1)*driving_speed
    v_theta = joystick.get_axis(2)*5
    shoot_button = joystick.get_button(2)
    auto_aim_button = joystick.get_button(0)

    x += vx*dt
    y += vy*dt
    theta += v_theta*dt

    # pygame.transform.rotate(sample_surface, theta)

    pygame.draw.line(screen, (0, 0, 0), (x, y), objects.get_forward_vector(
        x, y, 10, theta), 2)

    if (shoot_button == 1):
        v_shot, theta_v, theta_h = get_shot_params(x, y)
        print(v_shot, theta_v, theta_h)
        v_shot, theta_v, theta_h = get_moving_shot_params(
            v_shot, theta_v, theta_h, -vx/2, -vy/2)
        print(v_shot, theta_v, theta_h, vx, vy)
        theta = theta_h
        # print(v_shot/12, theta_v*180/math.pi, theta_h)
        # v_shot = 38*12  # ft/s
        # theta_v = 70*math.pi/180
        # theta_h = theta

        v_shot_x = v_shot * math.cos(theta_v) * math.cos(theta_h) * FSF
        v_shot_y = v_shot * math.cos(theta_v) * math.sin(theta_h) * FSF
        v_shot_z = v_shot * math.sin(theta_v)

        new_particle = objects.BallTrajectory(
            screen, (x, y, 0), (v_shot_x + vx, v_shot_y + vy, v_shot_z), dt)
        # new_particle = objects.Circle(screen, (x, y), ball_diameter*FSF)
        # new_particle.angle = theta + math.pi/2
        # new_particle.speed = 10*FSF
        my_particles.append(new_particle)

    if (auto_aim_button == 1):
        x_c, y_c, angle = get_center_coordinates(x, y)
        d = math.sqrt(x_c**2 + y_c**2)/2
        print(d)
        theta = math.pi - angle

    pygame.draw.polygon(screen, (0, 0, 0), objects.get_square_polygon_points(
        x, y, 29*FSF*8, theta), 1)

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
