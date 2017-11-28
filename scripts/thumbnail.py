# -*- coding: utf-8 -*-
#

import argparse
import os
import random
import cv2
import numpy as np

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument('--input', '-i', required=True)
    p.add_argument('--output', '-o', default='thumb.png')
    p.add_argument('--matrix', default='5x5')
    p.add_argument('--size', default='471x496')
    args = p.parse_args()
    return args

def get_files(target_path):
    files = []
    path = target_path
    for dirpath, dirs, files_ in os.walk(path):
        for fname in files_:
            if fname.endswith('.jpg'):
                f = os.path.join(dirpath, fname)
                files.append(f)
    #
    return files

def make_thumbnail(args):
    in_path = args.input
    output = args.output
    len_path =len(in_path)
    files = get_files(in_path)
    m = args.matrix.split('x')
    x, y = int(m[0]), int(m[1])
    m = x * y
    random.shuffle(files)
    y_imgs = []
    for yy in range(y):
        x_imgs = []
        for xx in range(x):
            idx = xx + yy * x
            fname = files[idx]
            img = cv2.imread(fname)
            x_imgs.append(img)
        x_imgs = np.hstack(x_imgs)
        y_imgs.append(x_imgs)
    y_imgs = np.vstack(y_imgs)
    return y_imgs
        

def main():
    args = get_args()
    img = make_thumbnail(args)
    s = args.size.split('x')
    x, y = int(s[0]), int(s[1])
    out_img = cv2.resize(img, (x, y))
    cv2.imwrite(args.output, out_img)

if __name__ == '__main__':
    main()
