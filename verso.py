import argparse
import sys

from pathlib import Path

import cv2
import numpy as np
import yaml

from natsort import natsorted

from constants import KEY_CANCEL, VALID_IMG_SUFFIXES


def decide_image(img, options):
    cond = True
    while cond:
        cv2.imshow('IMG', img)
        choice = cv2.waitKey(0)
        choice = chr(choice & 255)
        if choice in [*options, KEY_CANCEL]:
            cond = False
    return choice


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path_to_images',
        type=Path,
    )
    parser.add_argument(
        '--output',
        type=Path,
    )
    parser.add_argument(
        '--choices',
        nargs='+',
        default='s,d,k'
    )
    parser.add_argument(
        '--masks',
        type=Path,
    )
    args = parser.parse_args()

    size = 512
    images = [
        img
        for img
        in args.path_to_images.iterdir()
        if img.suffix in VALID_IMG_SUFFIXES
    ]
    images = natsorted(images)

    if args.masks:
        masks = [
            img
            for img
            in args.masks.iterdir()
            if img.suffix in VALID_IMG_SUFFIXES
        ]
        masks = [
            mask
            for mask
            in masks
            if mask.name in [
                    img.name
                    for img
                    in images
            ]
        ]
        masks = natsorted(masks)

    choices = {key: [] for key in args.choices}

    for i, image in enumerate(images):
        try:
            img = cv2.imread(str(image))
            img = cv2.resize(img, (size, size))
            if masks:
                mask = cv2.imread(str(masks[i]))
                mask = cv2.resize(mask, (size, size))
                img = np.concatenate((img, mask), axis=1)
                choice = decide_image(img, ['s','d','k'])
                if choice == KEY_CANCEL:
                    break
                else:
                    choices[choice] += [str(image)]
        except Exception as e:
            # TODO: proper error handling
            print(e)

    if args.output:
        with open(args.output, 'w') as f:
            yaml.dump(choices,f, sort_keys=False)
