# Copyright (c) 2022 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import cv2
import numpy as np
import time

import paddlers.utils.logging as logging
from paddlers.utils import is_pic



def visualize_detection(image, result, selectlabel, threshold=0.5, save_dir='./',
                        color=None):
    """
        Visualize bbox and mask results
    """

    if isinstance(image, np.ndarray):
        image_name = str(int(time.time() * 1000)) + '.jpg'
    else:
        image_name = os.path.split(image)[-1]
        image = cv2.imread(image)
    image = draw_bbox_mask(image, result, selectlabel, threshold=threshold, color_map=color)
    if save_dir is not None:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        out_path = os.path.join(save_dir, 'visualize_{}'.format(image_name))
        cv2.imwrite(out_path, image)
        logging.info('The visualized result is saved at {}'.format(out_path))
    else:
        return image




def get_color_map_list(num_classes):
    """ Returns the color map for visualizing the segmentation mask,
        which can support arbitrary number of classes.
    Args:
        num_classes: Number of classes
    Returns:
        The color map
    """
    color_map = num_classes * [0, 0, 0]
    for i in range(0, num_classes):
        j = 0
        lab = i
        while lab:
            color_map[i * 3] |= (((lab >> 0) & 1) << (7 - j))
            color_map[i * 3 + 1] |= (((lab >> 1) & 1) << (7 - j))
            color_map[i * 3 + 2] |= (((lab >> 2) & 1) << (7 - j))
            j += 1
            lab >>= 3
    color_map = [color_map[i:i + 3] for i in range(0, len(color_map), 3)]
    return color_map


def draw_bbox_mask(image, results, selectlabel, threshold=0.5, color_map=None):
    _SMALL_OBJECT_AREA_THRESH = 1000
    height, width = image.shape[:2]
    default_font_scale = max(np.sqrt(height * width) // 900, .5)
    linewidth = max(default_font_scale / 40, 2)

    labels = list()
    for dt in results:
        if dt['category'] not in labels:
            labels.append(dt['category'])
    
    labels = list(set(labels).intersection(set(selectlabel)))
    

    if color_map is None:
        color_map = get_color_map_list(len(labels) + 2)[2:]
    # else:
    #     color_map = np.asarray(color_map)
    #     if color_map.shape[0] != len(labels) or color_map.shape[1] != 3:
    #         raise Exception(
    #             "The shape for color_map is required to be {}x3, but recieved shape is {}x{}.".
    #             format(len(labels), color_map.shape))
    #     if np.max(color_map) > 255 or np.min(color_map) < 0:
    #         raise ValueError(
    #             " The values in color_map should be within 0-255 range.")

    keep_results = []
    areas = []
    for dt in results:
        cname, bbox, score = dt['category'], dt['bbox'], dt['score']
        if score < threshold and cname not in labels:
            continue
        keep_results.append(dt)
        areas.append(bbox[2] * bbox[3])
    areas = np.asarray(areas)
    sorted_idxs = np.argsort(-areas).tolist()
    keep_results = [keep_results[k]
                    for k in sorted_idxs] if keep_results else []
    cla2la = {
        'playground':0,
        'oiltank':1,
        'aircraft':2,
        'overpass':3
    }

    for dt in keep_results:
        cname, bbox, score = dt['category'], dt['bbox'], dt['score']
        bbox = list(map(int, bbox))
        xmin, ymin, w, h = bbox
        xmax = xmin + w
        ymax = ymin + h

        # color = tuple(map(int, color_map[labels.index(cname)]))
        color = tuple(map(int, color_map[cla2la[cname]]))
        # draw bbox
        image = cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color,
                              linewidth)

        # draw mask
        if 'mask' in dt:
            mask = dt['mask'] * 255
            image = image.astype('float32')
            alpha = .7
            w_ratio = .4
            color_mask = np.asarray(color, dtype=int)
            for c in range(3):
                color_mask[c] = color_mask[c] * (1 - w_ratio) + w_ratio * 255
            idx = np.nonzero(mask)
            image[idx[0], idx[1], :] *= 1.0 - alpha
            image[idx[0], idx[1], :] += alpha * color_mask
            image = image.astype("uint8")
            contours = cv2.findContours(
                mask.astype("uint8"), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE)[-2]
            image = cv2.drawContours(
                image,
                contours,
                contourIdx=-1,
                color=color,
                thickness=1,
                lineType=cv2.LINE_AA)

        # draw label
        text_pos = (xmin, ymin)
        instance_area = w * h
        if (instance_area < _SMALL_OBJECT_AREA_THRESH or h < 40):
            if ymin >= height - 5:
                text_pos = (xmin, ymin)
            else:
                text_pos = (xmin, ymax)
        height_ratio = h / np.sqrt(height * width)
        font_scale = (np.clip((height_ratio - 0.02) / 0.08 + 1, 1.2,
                              2) * 0.5 * default_font_scale)
        text = "{} {:.2f}".format(cname, score)
        (tw, th), baseline = cv2.getTextSize(
            text,
            fontFace=cv2.FONT_HERSHEY_DUPLEX,
            fontScale=font_scale,
            thickness=1)
        image = cv2.rectangle(
            image,
            text_pos, (text_pos[0] + tw, text_pos[1] + th + baseline),
            color=color,
            thickness=-1)
        image = cv2.putText(
            image,
            text, (text_pos[0], text_pos[1] + th),
            fontFace=cv2.FONT_HERSHEY_DUPLEX,
            fontScale=font_scale,
            color=(255, 255, 255),
            thickness=1,
            lineType=cv2.LINE_AA)

    return image
