import sys
from PIL import Image
big_img = Image.open('.\\images\\big.png')
small_img = Image.open('.\\images\\small.png')
def my_nearest_resize(big_img, small_img):
    big_w, big_h = big_img.size 
    small_w, small_h = small_img.size 
    dst_im = big_img.copy()
    stepx = big_w/small_w
    stepy = big_h/small_h
    for i in range(0, small_w):
        for j in range(0, small_h):
            map_x = int( i*stepx + stepx*0.5 )
            map_y = int( j*stepy + stepy*0.5 )
            if map_x < big_w and map_y < big_h :
                dst_im.putpixel((map_x, map_y), small_img.getpixel((i, j)))
    return dst_im
my_nearest_resize(big_img, small_img)
dst_im = my_nearest_resize(big_img, small_img)
dst_im.save('.\\images\\ETO.png')
