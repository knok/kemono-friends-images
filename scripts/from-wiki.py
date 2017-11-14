# -*- coding: utf-8 -*-
#

import argparse
from bs4 import BeautifulSoup
import urllib.request
import urllib.parse
import time
import os

attr_dict = {
    'パッション': 0, 'ピュア': 1, 'クール': 2
    }

attrval_dict = {0: 'passion', 1: 'pure', 2: 'cool'}
extimg_dict = {'プロフィール': 'prof', '最大LV': 'maxlevel'}

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--wait', '-w', type=int, default=5)
    parser.add_argument('--base-url',
                        default='https://kemono-friends.gamerch.com')
    parser.add_argument('--start-url',
                        default='https://kemono-friends.gamerch.com/%E3%82%AD%E3%83%A3%E3%83%A9%E4%B8%80%E8%A6%A7')
    parser.add_argument('--output-dir', '-o', default='save')
    parser.add_argument('--save-all', default=False, action='store_true')
    args = parser.parse_args()
    return args

def get_from_start_page(args):
    print("fetch: %s" % args.start_url)
    html = urllib.request.urlopen(args.start_url)
    soup = BeautifulSoup(html, 'lxml')
    elems = soup.select('a[href^="/"]')
    vals = []
    for e in elems:
        p = e.parent
        if p.name == 'td':
            vals.append(e)
    time.sleep(args.wait)
    return vals

def get_char_info(page_url):
    print("fetch: %s" % page_url)
    html = urllib.request.urlopen(page_url)
    soup = BeautifulSoup(html, 'lxml')
    imgs = soup.select('a[href$=".jpg"]')
    attr_list = soup.select('span.ui_wikidb_title')
    for a in attr_list:
        a_text = a.text
        if a_text == 'レアリティ':
            r = a.findNext()
            rarity = int(r.text[-1])
        elif a_text == '属性':
            r = a.findNext()
            attr = attr_dict[r.text]
    imgs_urls = []
    for i in imgs:
        imgs_urls.append(i['href'])
    return imgs_urls, rarity, attr

def get_each_images(args, vals):
    for v in vals:
        c = v['href']
        page_url = args.base_url + urllib.parse.quote(c)
        img_urls, rarity, attr = get_char_info(page_url)
        print('rarity: %d, attr: %s' % (rarity, attr))
        target_dir = os.path.join(args.output_dir, attrval_dict[attr], str(rarity))
        os.makedirs(target_dir, exist_ok=True)
        for i, img_url in enumerate(img_urls):
            fname = os.path.basename(img_url)
            if i > 0 and args.save_all is False:
                print('save only first image, skip %s' % fname)
                continue
            fname = os.path.join(target_dir, fname)
            if os.path.exists(fname):
                print('skip %s' % fname)
                continue
            with open(fname, 'wb') as f:
                raw_img = urllib.request.urlopen(img_url).read()
                f.write(raw_img)
            print('%s saved' % fname)
            time.sleep(args.wait)

def main():
    args = get_args()
    vals = get_from_start_page(args)
    get_each_images(args, vals)

if __name__ == '__main__':
    main()


