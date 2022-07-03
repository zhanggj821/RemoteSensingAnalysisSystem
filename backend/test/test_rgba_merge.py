import cv2 as cv
import numpy as np

image_befor_path_1 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/changedetection/A_train_4_0_3.png'
image_after_path_1 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/changedetection/B_train_4_0_3.png'
rgba_path = '/home/guangjun/PaddleRS/flask_paddlers/test/alpha_img.png'
im_befor_1 = cv.imread(image_befor_path_1)
im_after_1 = cv.imread(image_after_path_1, cv.IMREAD_UNCHANGED)
alpha_img = cv.imread(rgba_path, cv.IMREAD_UNCHANGED)

def add_alpha_channel(img):
    """ 为jpg图像添加alpha通道 """
 
    b_channel, g_channel, r_channel = cv.split(img) # 剥离jpg图像通道
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255 # 创建Alpha通道
 
    img_new = cv.merge((b_channel, g_channel, r_channel, alpha_channel)) # 融合通道
    return img_new

im_after_1 = add_alpha_channel(im_after_1)


alpha_png = alpha_img[:,:,3] / 255.0
alpha_jpg = 1- alpha_png
for c in range(0,3):
        im_after_1[:, :, c] = ((alpha_jpg*im_after_1[:,:,c]) + (alpha_png*alpha_img[:,:,c]))



cv.imwrite('./merge_rgba_2.png', im_after_1)