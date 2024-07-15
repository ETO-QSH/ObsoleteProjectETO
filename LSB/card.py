

from PIL import Image
new = Image.new('RGB', (61, 4))

maps = [(127, 178, 56), (247, 233, 163), (199, 199, 199), (255, 0, 0), (160, 160, 255), (167, 167, 167), (0, 124, 0), 
        (255, 255, 255), (164, 168, 184), (151, 109, 77), (112, 112, 112), (64, 64, 255), (143, 119, 72), (255, 252, 245), 
        (216, 127, 51), (178, 76, 216), (102, 153, 216), (229, 229, 51), (127, 204, 25), (242, 127, 165), (76, 76, 76), 
        (153, 153, 153), (76, 127, 153), (127, 63, 178), (51, 76, 178), (102, 76, 51), (102, 127, 51), (153, 51, 51), 
        (25, 25, 25), (250, 238, 77), (92, 219, 213), (74, 128, 255), (0, 217, 58), (129, 86, 49), (112, 2, 0), 
        (209, 177, 161), (159, 82, 36), (149, 87, 108), (112, 108, 138), (186, 133, 36), (103, 117, 53), 
        (160, 77, 78), (57, 41, 35), (135, 107, 98), (87, 92, 92), (122, 73, 88), (76, 62, 92), (76, 50, 35), 
        (76, 82, 42), (142, 60, 46), (37, 22, 16), (189, 48, 49), (148, 63, 97), (92, 25, 29), (22, 126, 134), 
        (58, 142, 140), (86, 44, 62), (20, 180, 133), (86, 86, 86), (186, 150, 126), (127, 167, 150)]

for x in range(len(maps)):
    for y in [180, 220, 255, 135]:
        tip = []
        for z in range(3):
            tip.append(int(maps[x][z] * y / 255))
        new.putpixel((x, [180, 220, 255, 135].index(y)), tuple(tip))

new.save('.\\images\\scc.png')