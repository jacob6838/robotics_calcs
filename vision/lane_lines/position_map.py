import pixel_angles

IMAGE_CENTER = (4, -1)

# key = [
#     [[143, 123],    [237, 123],     [333, 125],     [424, 126],     [523, 126], ],
#     [[106, 127],    [219, 129],     [332, 131],     [443, 131],     [561, 132], ],
#     [[43, 136],     [187, 139],     [332, 140],     [476, 140],     [624, 143], ],
#     [[None, None],  [129, 156],     [333, 159],     [532, 160],     [None, None], ],
#     [[None, None],  [7, 195],       [333, 198],     [None, None],   [None, None], ],
#     [[None, None],  [None, None],   [333, 373],     [None, None],   [None, None], ],
# ]

# out = [
#     [[12.93, 4.26], [11.98, 1.87],  [11.16, -0.27], [10.79, -2.11], [10.79, -4.17], ],
#     [[10.44, 4.27], [9.81, 1.86],   [9.25, -0.21],  [9.25, -2.14],  [8.99, -4.18], ],
#     [[8.09, 4.38],  [7.52, 1.88],   [7.35, -0.17],  [7.35, -2.16],  [6.87, -4.13], ],
#     [[None, None],  [5.36, 1.95],   [5.1, -0.13],   [5.02, -2.03],  [None, None], ],
#     [[None, None],  [3.2, 1.99],    [3.1, -0.08],   [None, None],   [None, None], ],
#     [[None, None],  [None, None],   [1.04, -0.03],  [None, None],   [None, None], ]
# ]

# err = [
#     [[11.76, 0.24], [11.76, -1.56], [1.92, -3.24],  [-2.52, -1.32], [-2.52, -2.04], ],
#     [[17.28, 3.24], [9.72, -1.68],  [3.0, -2.52],   [3.0, -1.68],   [-0.12, -2.16], ],
#     [[13.08, 4.56], [6.24, -1.44],  [4.2, -2.04],   [4.2, -1.92],   [-1.56, -1.56], ],
#     [[None, None],  [4.32, -0.6],   [1.2, -1.56],   [0.24, -0.36],  [None, None], ],
#     [[None, None],  [2.4, -0.12],   [1.2, -0.96],   [None, None],   [None, None], ],
#     [[None, None],  [None, None],   [0.48, -0.36],  [None, None],   [None, None], ]
# ]

key = [
    [[359, 509],    [811, 519],    [1271, 526],    [1729, 528],    [2186, 532], ],
    [[81, 553],     [678, 559],    [1265, 566],     [1854, 569],    [2449, 574], ],
    [[None, None],  [432, 632],    [1259, 645],    [2085, 645],    [None, None], ],
    [[None, None],  [None, None],  [1258, 818],     [None, None],   [None, None], ],
    [[None, None],  [None, None],  [1256, 1686],     [None, None],   [None, None], ],
]

out = [
    [[0.64, -0.05], [0.62, -0.69], [0.61, -5.68], [0.6, 1.62], [0.6, 0.76]],
    [[0.56, 0.26], [0.55, -0.4], [0.54, -4.7], [0.53, 1.08], [0.52, 0.54]],
    [[None, None], [0.44, -0.09], [0.42, -3.49], [0.42, 0.61], [None, None]],
    [[None, None], [None, None], [0.25, -2.01], [None, None], [None, None]],
    [[None, None], [None, None], [-0.14, 1.09], [None, None], [None, None]]
]


def index_to_position(i, j):
    position = j * 2, (4-i) * 2
    relative_position = [position[k] - IMAGE_CENTER[k] for k in range(2)]
    relative_position[0] = -relative_position[0]
    return relative_position


# print(index_to_position(0, 0))
# print(index_to_position(0, 2))
# print(index_to_position(0, 4))


out = []
for row in key:
    row_out = []
    for col in row:
        if not col[0] or not col[1]:
            col_out = [None, None]
        else:
            col_out = [round(i / 0.0254 / 12, 2) for i in pixel_angles.get_real_position(col[0] /
                                                                                         pixel_angles.scale, col[1]/pixel_angles.scale, 0, (0, 0), (0, -15), 0.175)]
            print([i / 0.0254 / 12 for i in pixel_angles.get_real_position(col[0] /
                                                                           pixel_angles.scale, col[1]/pixel_angles.scale, 0, (0, 0), (0, -15), 0.175)])
        row_out.append(col_out)
    out.append(row_out)

print(out)

err = []
for i, row in enumerate(out):
    row_err = []
    for j, col in enumerate(row):
        if not col[0] or not col[1]:
            col_err = [None, None]
        else:
            pos = index_to_position(i, j)
            print(i, j, pos)
            col_err = [round((col[k] - pos[abs(k-1)])*12, 2) for k in range(2)]
        row_err.append(col_err)
    err.append(row_err)

print(err)
