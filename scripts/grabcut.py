# -*- coding: utf-8 -*-

import re, os
import argparse
import numpy as np
import cv2
#import matplotlib.pyplot as plt

values = {'rect': (210, 50, 230, 400),
          'face_pos': (280, 120, 360, 200)}

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
    # filter files

def filtering_files(files, regex='cool/5/'):
    allow_regex = re.compile(regex)
    filtered = []
    for f in files:
        if allow_regex.search(f):
            filtered.append(f)

    return filtered

def img_clip(img):
    h, w, c = img.shape
    x0 = int(w * 0.45)
    y0 = int(h * 0.76)
    clip = img[0:y0, 0:x0, :]
    return clip

def do_grabcut(fname):
    img = cv2.imread(fname)
    cimg = img_clip(img)
    mask = np.zeros(cimg.shape[:2], dtype=np.uint8)
    rect = values['rect']
    bgModel = np.zeros((1, 65), np.float64)
    fgModel = np.zeros((1, 65), np.float64)
    #import pdb; pdb.set_trace()
    cv2.grabCut(cimg, mask, rect, bgModel, fgModel, 5, cv2.GC_INIT_WITH_RECT)
    x1, y1, x2, y2 = values['face_pos']
    cv2.rectangle(mask, (x1, y1), (x2, y2), 1, -1)
    cv2.grabCut(cimg, mask, None, bgModel, fgModel, 5, cv2.GC_INIT_WITH_MASK)
    out = cimg.copy()
    out[np.where((mask == 0) | (mask == 2))] = 255
    return out

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument('--input', '-i', default='fixed')
    p.add_argument('--output', '-o', default='grabcut')
    args = p.parse_args()
    return args

def main():
    args = get_args()
    files = get_files(args.input)
    inpath_len = len(args.input)
    for f in files:
        img = do_grabcut(f)
        bfname = f[inpath_len+1:]
        out_fname = os.path.join(args.output, bfname)
        out_dir = os.path.dirname(out_fname)
        os.makedirs(out_dir, exist_ok=True)
        cv2.imwrite(out_fname, img)
        print(out_fname)

if __name__ == '__main__':
    main()
