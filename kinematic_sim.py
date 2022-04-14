import math
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

# v0 = 11  # m/s
# theta0 = 50  # degrees
mass = 280/1000  # kg
diameter = 20/100  # m
r = diameter/2
dt = 0.001  # seconds


# constants
g = 9.8  # m/s
p = 1.225  # kg/m^3
mu = 1.8*(10**-5)


def get_energy(v, w, h):
    return .5*mass*v**2 + .5*(2/3)*mass*(r**2)*(w**2) + mass*g*h


def vacuum(v0, theta0, drag_coefficient, spin_coefficient):
    v0 = v0 * .3048
    theta0 = theta0 * math.pi/180
    # Initial Conditions
    x = 0
    y = 0
    vx = v0*math.cos(theta0)
    vy = v0*math.sin(theta0)

    vacuum_coordinates = []
    while y >= 0:
        x += vx*dt
        y += vy*dt

        vx = vx
        vy = vy - g*dt
        vacuum_coordinates.append([x*3.28, y*3.28])
        # print(x, y)
    vacuum_coordinates = list(map(list, zip(*vacuum_coordinates)))

    # print(x, y)

    # print("------------- Vacuum -------------")
    # print(x*3.28, y*3.28)
    # v = math.sqrt(vx**2 + vy**2)
    # print("final v", v, vx, vy)
    return vacuum_coordinates


def drag(v0, theta0, drag_coefficient, spin_coefficient):
    v0 = v0 * .3048
    theta0 = theta0 * math.pi/180
    # Initial Conditions
    x = 0
    y = 0
    vx = v0*math.cos(theta0)
    vy = v0*math.sin(theta0)
    c = (math.pi/16) * p * diameter**2  # kg/m^3*m^2 = kg/m
    # print("C:", c)

    drag_coordinates = []
    while y >= 0:
        x += vx*dt
        y += vy*dt

        # print(vx, vy)
        v = math.sqrt(vx**2 + vy**2)
        theta = math.atan2(vy, vx)
        Fd = c * v**2 * drag_coefficient
        # print(v, theta*180/math.pi, Fd)

        vx = vx - Fd*math.cos(theta)/mass*dt
        vy = vy - g*dt - Fd*math.sin(theta)/mass*dt
        drag_coordinates.append([x*3.28, y*3.28])
        # print(x, y)
    drag_coordinates = list(map(list, zip(*drag_coordinates)))

    # print("------------- Drag -------------")
    # print(x*3.28, y*3.28)
    # v = math.sqrt(vx**2 + vy**2)
    # print("final v", v, vx, vy)
    return drag_coordinates


def spin(v0, theta0, drag_coefficient, spin_coefficient):
    v0 = v0 * .3048
    theta0 = theta0 * math.pi/180
    # Initial Conditions
    x = 0
    y = 0
    vx = v0*math.cos(theta0)
    vy = v0*math.sin(theta0)
    c = (math.pi/16) * p * diameter**2  # kg/m^3*m^2 = kg/m
    d = 2*math.pi*p*(r)**2/r
    b = 4.1*10**-4*2/4
    # print("C:", c)
    # print("Constants", b, d)
    e = 3*math.pi*mu*r/(2*mass)
    # print(e)

    w = v0/r
    wf = 0*v0/r
    ti = 0
    tf = 2


    spin_coordinates = []
    time_elapsed = 0
    while y >= 0:

        x += vx*dt
        y += vy*dt

        v = math.sqrt(vx**2 + vy**2)
        theta = math.atan2(vy, vx)
        Fd = c * v**2 * drag_coefficient
        # print(v, theta*180/math.pi, Fd)

        energy = get_energy(v, w, y)
        # print(energy)

        w = w - e*w*dt

        Fm = b * v * w * spin_coefficient
        # print("magnus", v, Fm/mass*dt)

        # print("initial v", v, vx, vy)
        vx = vx - Fd*math.cos(theta)/mass*dt + Fm * \
            math.cos(theta+math.pi/2)/mass*dt
        vy = vy - g*dt - Fd*math.sin(theta)/mass*dt + Fm * \
            math.sin(theta+math.pi/2)/mass*dt  # + Fm/mass*dt
        # v = math.sqrt(vx**2 + vy**2)
        # print("final v", v, vx, vy)
        # print(x, y)
        spin_coordinates.append([x*3.28, y*3.28])
        time_elapsed += dt
        # break
    spin_coordinates = list(map(list, zip(*spin_coordinates)))

    # print("------------- Spin -------------")
    # print(x*3.28, y*3.28)
    # v = math.sqrt(vx**2 + vy**2)
    # print("final v", v, vx, vy, w)
    # print(time_elapsed)
    return spin_coordinates


# The function to be called anytime a slider's value changes
def update(val):
    global front_line
    global back_line
    vel = vel_slider.val
    theta = angle_slider.val
    drag_coeff = drag_slider.val
    spin_coeff = spin_slider.val
    distance = distance_slider.val
    front_line.remove()
    back_line.remove()
    front_line = ax.axvline(x=distance)
    back_line = ax.axvline(x=distance + 4)
    vacuum_data = vacuum(vel, theta, drag_coeff, spin_coeff)
    vacuum_line.set_xdata(vacuum_data[0])
    vacuum_line.set_ydata(vacuum_data[1])
    drag_data = drag(vel, theta, drag_coeff, spin_coeff)
    drag_line.set_xdata(drag_data[0])
    drag_line.set_ydata(drag_data[1])
    spin_data = spin(vel, theta, drag_coeff, spin_coeff)
    spin_line.set_xdata(spin_data[0])
    spin_line.set_ydata(spin_data[1])

    fig.canvas.draw_idle()


fig, ax = plt.subplots(1, 1)

goal_line = ax.axhline(y=6.5)
max_height = ax.axhline(y=18)
front_line = ax.axvline(x=6)
back_line = ax.axvline(x=6+4)

vacuum_line, = ax.plot(*vacuum(35, 60, 1, 1), lw=2)
# plt.subplots_adjust(bottom=0.35)
drag_line, = ax.plot(*drag(35, 60, 1, 1), lw=2)
# plt.subplots_adjust(bottom=0.35)
spin_line, = ax.plot(*spin(35, 60, 1, 1), lw=2)
plt.xlim([-5, 35])
plt.ylim([0, 30])
plt.subplots_adjust(bottom=0.35)

axfreq = plt.axes([0.25, 0, 0.65, 0.03])
vel_slider = Slider(
    ax=axfreq,
    label='Velocity (ft/s)',
    valmin=0.1,
    valmax=60,
    valinit=35,
)
axfreq = plt.axes([0.25, 0.05, 0.65, 0.03])
angle_slider = Slider(
    ax=axfreq,
    label='Angle (degrees)',
    valmin=0,
    valmax=89,
    valinit=60,
)
axfreq = plt.axes([0.25, 0.1, 0.65, 0.03])
drag_slider = Slider(
    ax=axfreq,
    label='Drag Coefficient',
    valmin=0.01,
    valmax=2,
    valinit=1,
)
axfreq = plt.axes([0.25, 0.15, 0.65, 0.03])
spin_slider = Slider(
    ax=axfreq,
    label='Spin Coefficient',
    valmin=0.01,
    valmax=2,
    valinit=1,
)
axfreq = plt.axes([0.25, 0.2, 0.65, 0.03])
distance_slider = Slider(
    ax=axfreq,
    label='Distance (ft)',
    valmin=0,
    valmax=30,
    valinit=6,
)


vel_slider.on_changed(update)
angle_slider.on_changed(update)
drag_slider.on_changed(update)
spin_slider.on_changed(update)
distance_slider.on_changed(update)

ax.set_xlabel('Position (ft)')


# plt.plot(vacuum_coordinates[0], vacuum_coordinates[1], drag_coordinates[0],
#          drag_coordinates[1], spin_coordinates[0], spin_coordinates[1])
# plt.legend(['vacuum', 'drag', 'spin+drag'])
plt.title(
    f"Ball paths")
plt.show()
