import numpy as np
import cv2 as cv
import sys
sys.path.append('/home/guangjun/PaddleRS')
import paddle
import paddlers as pdrs
from paddlers import transforms as T
import numpy as np
import os.path as osp
from skimage.io import imread, imsave

from flask_paddlers.myutils.crop import crop_img, recons_prob_map, quantize


predictor = pdrs.deploy.Predictor('/home/guangjun/PaddleRS/flask_paddlers/infer_model/inference_changedetection', use_gpu=True)
image_befor_path_1 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/changedetection/A_train_4_0_3.png'
image_after_path_1 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/changedetection/B_train_4_0_3.png'

im_befor_1 = cv.imread(image_befor_path_1)
im_after_1 = cv.imread(image_after_path_1)

imgs = (im_befor_1, im_after_1)

trans = T.Compose([
    T.Normalize()
])


result = predictor.predict(img_file=imgs, transforms=trans)
label_map = result[0]['label_map']

def get_lut():
    lut = np.zeros((2,4), dtype=np.uint8)
    lut[0] = [0, 0, 0, 0]
    lut[1] = [0, 0, 255, 60]
    return lut

lut = get_lut()
im = lut[label_map]
# img_rgba = cv.merge(im)

cv.imwrite('./alpha_img.png', im)

