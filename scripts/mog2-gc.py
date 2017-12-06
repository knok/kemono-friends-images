# -*- coding: utf-8 -*-

import re, os
import argparse
import numpy as np
import cv2

values = {'rect': (155, 20, 340, 450), # (495, 470)
          'face_pos': (288, 120, 355, 200),
          'clip': (0.45, 0.73),
          'opening_iter': 1,
          'iter': 4,
          'img_area': (155, 20, 495, 450)}

def get_args():
    p = argparse.ArgumentParser()
    p.add_argument('--input', '-i', default='fixed')
    p.add_argument('--output', '-o', default='mog2-gc')
    p.add_argument('--mark-face', default=False, action='store_true')
    p.add_argument('--bad-output', default='bad-mog2')
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

def filtering_files(files, regex='cool/5/'):
    allow_regex = re.compile(regex)
    filtered = []
    for f in files:
        if allow_regex.search(f):
            filtered.append(f)

    return filtered

def get_filterd_files(files):
    attr = 'cool passion pure'.split()
    rarelity = '[12] 3 4 5'.split()
    for a in attr:
        for r in rarelity:
            pat = '%s/%s/' % (a, r)
            yield filtering_files(files, pat)

def img_clip(img):
    h, w, c = img.shape
    x0 = int(w * values['clip'][0])
    y0 = int(h * values['clip'][1])
    clip = img[0:y0, 0:x0, :]
    return clip

def find_whole_rect(cts):
    min_x, min_y = 10000, 10000
    max_x, max_y = -1, -1
    for c in cts:
        x, y, w, h = cv2.boundingRect(c)
        xx = x + w
        yy = y + h
        min_x = x if min_x > x else min_x
        min_y = y if min_y > y else min_y
        max_x = xx if max_x < xx else max_x
        max_y = yy if max_y < yy else max_y
    return [min_x, min_y, max_x, max_y]

def get_area_by_mog2(idx, imgs):
    fgbd = cv2.createBackgroundSubtractorMOG2()
    cimgs = imgs.copy()
    target_img = cimgs.pop(idx)
    for i in cimgs:
        fgmask = fgbd.apply(i)
    fgmask = fgbd.apply(target_img)

    kernel = np.ones((5, 5), np.uint8)
    dmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel, iterations=values['opening_iter'])
    dmask = cv2.dilate(dmask, kernel, iterations=values['iter'])
    ret, thresh = cv2.threshold(dmask, 127, 255, 0)
    img ,cts, hier = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    area = find_whole_rect(cts)
    w, h = area[2]-area[0], area[3]-area[1]
    area.extend([w, h])
    return area

def read_images(files):
    imgs = []
    for f in files:
        img = cv2.imread(f)
        cimg = img_clip(img)
        imgs.append(cimg)
    return imgs

def get_output_path(args, fname):
    inpath_len = len(args.input)
    bfname = fname[inpath_len+1:]
    out_fname = os.path.join(args.output, bfname)
    out_dir = os.path.dirname(out_fname)
    os.makedirs(out_dir, exist_ok=True)
    return out_fname

def get_bad_output_path(args, fname):
    inpath_len = len(args.input)
    bfname = fname[inpath_len+1:]
    out_fname = os.path.join(args.bad_output, bfname)
    out_dir = os.path.dirname(out_fname)
    os.makedirs(out_dir, exist_ok=True)
    return out_fname

def area_eq_imgsize(area, img):
    h, w, _ = img.shape
    return area[2] == w and area[3] == h

def copy_image(args, fname, img):
    out_fname = get_bad_output_path(args, fname)
    cv2.imwrite(out_fname, img)
    return

def do_grabcut(args, files):
    imgs = read_images(files)
    for i, fname in enumerate(files):
        cimg = imgs[i]
        area = get_area_by_mog2(i, imgs)
        if area_eq_imgsize(area, cimg):
            print("area is whole image %s" % fname)
            x1, y1, x2, y2 = values['img_area']
            out = cimg[y1:y2, x1:x2, :]
            copy_image(args, fname, out)
            continue
        mask = np.zeros(cimg.shape[:2], dtype=np.uint8)
        rect = (area[0], area[1], area[4], area[5])
        bgModel = np.zeros((1, 65), np.float64)
        fgModel = np.zeros((1, 65), np.float64)
        cv2.grabCut(cimg, mask, rect, bgModel, fgModel, 5, cv2.GC_INIT_WITH_RECT)
        if args.mark_face:
            x1, y1, x2, y2 = values['face_pos']
            cv2.rectangle(mask, (x1, y1), (x2, y2), 1, -1)
            cv2.grabCut(cimg, mask, None, bgModel, fgModel, 5, cv2.GC_INIT_WITH_MASK)
        out = cimg.copy()
        out[np.where((mask == 0) | (mask == 2))] = 255
        x1, y1, x2, y2 = values['img_area']
        out = out[y1:y2, x1:x2, :]
        out_fname = get_output_path(args, fname)
        cv2.imwrite(out_fname, out)
        print(out_fname)

def main():
    args = get_args()
    all_files = get_files(args.input)
    for files in get_filterd_files(all_files):
        do_grabcut(args, files)


if __name__ == '__main__':
    main()

