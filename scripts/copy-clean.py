# -*- coding: utf-8 -*-
#

import os
import cv2
import numpy as np
import argparse
import shutil

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument('--input', '-i', default='grabcut')
    p.add_argument('--output', '-o', default='gc-clean')
    args = p.parse_args()
    return args

def gen_files(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith('.jpg'):
                yield os.path.join(root, f)

#
def v_clean(img, pos):
    v_sum = img[:, pos, :].sum()
    v_avg = int(v_sum / img.shape[0] / 3)
    return v_avg >= 200

def h_clean(img, pos):
    h_sum = img[pos, :, :].sum()
    h_avg = int(h_sum / img.shape[1] / 3)
    return h_avg >= 200

def is_clean(fname):
    img = cv2.imread(fname)
    return v_clean(img, 0) and v_clean(img, -1) and h_clean(img, 0) and h_clean(img, -1)

def copy_img(fname, args):
    len_input = len(args.input)
    base_path = fname[len_input+1:]
    output_fname = os.path.join(args.output, base_path)
    output_dir = os.path.dirname(output_fname)
    os.makedirs(output_dir, exist_ok=True)
    shutil.copy2(fname, output_fname)
    print(output_fname)

def main():
    args = get_args()
    for fname in gen_files(args.input):
        if is_clean(fname):
            copy_img(fname, args)

if __name__ == '__main__':
    main()
