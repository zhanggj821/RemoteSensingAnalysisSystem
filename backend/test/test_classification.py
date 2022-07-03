from cProfile import label
from cgi import print_arguments
import sys
import os
from turtle import shape
sys.path.append('/home/guangjun/PaddleRS')
import paddle
import paddlers as pdrs
from paddlers import transforms as T
import numpy as np
import os.path as osp
import cv2

from flask_paddlers.myutils.crop import crop_img, recons_prob_map, quantize

def get_lut():
    lut = np.zeros((256,3), dtype=np.uint8)
    lut[0] = [255, 0, 0]
    lut[1] = [30, 255, 142]
    lut[2] = [60, 0, 255]
    lut[3] = [255, 222, 0]
    lut[4] = [0, 0, 0]
    return lut


def showimg(im, path,lut=None):
    if im.ndim == 3:
        im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    im = lut[im]
    cv2.imwrite(path, im)


predictor = pdrs.deploy.Predictor('/home/guangjun/PaddleRS/flask_paddlers/infer_model/inference_classification', use_gpu=True)


test_image_1 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/classification/3.jpg'
test_image_2 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/classification/12.jpg'
test_image_3 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/classification/59.jpg'

imgs = []
img1 = cv2.imread(test_image_1)
img2 = cv2.imread(test_image_2)
img3 = cv2.imread(test_image_3)
imgs = [img1, img2, img3]

trans = T.Compose([
    T.Resize(target_size=256),
    # 验证阶段与训练阶段的数据归一化方式必须相同
    T.Normalize(
        mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
])




results = predictor.predict(img_file=imgs, transforms=trans)


for index, result in enumerate(results): 
    pred_map = result['label_map']
    path = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/classification'
    savepath = os.path.join(path, 'infer_{}.jpg'.format(index))
    showimg(pred_map, savepath, lut = get_lut())





    


