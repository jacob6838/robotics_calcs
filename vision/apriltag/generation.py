import moms_apriltag as apt
import numpy as np
import imageio


if __name__ == '__main__':
    family = "tag36h10"
    shape = (1, 1)
    filename = "apriltag_target.png"
    size = 50

    tgt = apt.board(shape, family, size)
    imageio.imwrite(filename, tgt)