from cProfile import label
from cgi import print_arguments
import sys
import os
sys.path.append('/home/guangjun/PaddleRS')
import paddle
import paddlers as pdrs
from paddlers import transforms as T
import numpy as np
import os.path as osp
import cv2

from flask_paddlers.myutils.crop import crop_img, recons_prob_map, quantize


predictor = pdrs.deploy.Predictor('/home/guangjun/PaddleRS/flask_paddlers/infer_model/inference_extraction', use_gpu=True)

test_image_1 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/objectextraction/10228690_15.png'
test_image_2 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/objectextraction/img-10.png'
test_image_3 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/objectextraction/10978735_15.png'

# os.path.basename(test_image)


trans = T.Compose([
    T.Resize(target_size=1488),
    # 验证阶段与训练阶段的数据归一化方式必须相同
    T.Normalize(
        mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
])


img_1 = cv2.imread(test_image_1)
img_2 = cv2.imread(test_image_2)
img_3 = cv2.imread(test_image_3)

imgs = [img_1, img_2, img_3]

result = predictor.predict(img_file=imgs, transforms=trans)
# print(type(result))
# print(result.keys())
print(len(result))

for index in range(len(imgs)):
    pred_map = result[index]['label_map']    
    cv2.imwrite('../testimgs/objectextraction/infer' + str(index) +'.png', pred_map*255)
# cv2.imwrite('../testimgs/objectextraction/infer_img10_1.png', quantize(pred_score > 0.5))




