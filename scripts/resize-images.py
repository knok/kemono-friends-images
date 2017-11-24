# -*- coding:utf-8 -*-

import argparse
import os
from PIL import Image

candidate_size = [(1104, 621), (1136, 640), (1200, 674)]
target_size = (1104, 621)

def get_files(d):
    for dirpath, dirs, files in os.walk(d):
        for fname in files:
            if fname.endswith('jpg'):
                yield d, dirpath, fname

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument('--input', '-i', default='save')
    p.add_argument('--output', '-o', default='fixed')
    args = p.parse_args()
    return args

def main():
    args = get_args()
    path_len = len(args.input)
    for base, dname, fname in get_files(args.input):
        fullpath = os.path.join(dname, fname)
        img = Image.open(fullpath)
        w, h = img.size
        if (w, h) in candidate_size:
            rimg = img.resize(target_size)
            fname = fullpath[path_len+1:]
            out_fname = os.path.join(args.output, fname)
            out_dir = os.path.dirname(out_fname)
            os.makedirs(out_dir, exist_ok=True)
            rimg.save(out_fname, quality=100)
            print("saved %s" % out_fname)

if __name__ == '__main__':
    main()
