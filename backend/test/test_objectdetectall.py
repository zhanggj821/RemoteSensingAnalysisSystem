import sys
sys.path.append('/home/guangjun/PaddleRS')
import cv2 as cv
import paddle
import paddlers as pdrs
import numpy as np
import os.path as osp
from skimage.io import imread, imsave
from paddlers import transforms as T

from flask_paddlers.myutils.visualize import visualize_detection

from matplotlib import pyplot as plt
from PIL import Image

predictor = pdrs.deploy.Predictor('/home/guangjun/PaddleRS/flask_paddlers/infer_model/inference_detection_ppyolo/all', use_gpu=True)
trans = T.Compose([
            # 使用双三次插值将输入影像缩放到固定大小
            T.Resize(
                target_size=608, interp='CUBIC'
            ),
            # 验证阶段与训练阶段的归一化方式必须相同
            T.Normalize(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
            )
        ])

img_path_1 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/objectdect/aircraftoiltank_merge.jpg'
# img_path_2 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/objectdect/playground_22.jpg'
# img_path_3 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/objectdect/playground_30.jpg'
# img_1 = cv.imread(img_path_1)
# img_2 = cv.imread(img_path_2)
# img_3 = cv.imread(img_path_3)
# imgs = [img_1, img_2, img_3]

img = cv.imread(img_path_1)

result = predictor.predict(img_file=img, transforms=trans)

# print(len(result))
# bbox = result[0]['bbox']
# score = result[0]['score']
# category = result[0]['category']


# for index, im in enumerate(imgs):
#     vis = visualize_detection(
#         np.array(im), result[index], 
#         color=np.asarray([[0,255,0]], dtype=np.uint8), 
#         threshold=0.2, save_dir=None
#     )
#     cv.imwrite('vis_'+str(index)+'.jpg', vis)        
    

vis = visualize_detection(
                np.array(img), result, 
                color=np.asarray([[255,0,0],[230,255,0],[0,255,0],[0,0,255]], dtype=np.uint8), 
                threshold=0.5, save_dir=None
            )
cv.imwrite('vis1.jpg', vis)








    
