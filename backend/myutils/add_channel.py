import numpy as np
import cv2 as cv

def add_alpha_channel(img):
    """ 为jpg图像添加alpha通道 """
 
    b_channel, g_channel, r_channel = cv.split(img) # 剥离jpg图像通道
    alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255 # 创建Alpha通道
 
    img_new = cv.merge((b_channel, g_channel, r_channel, alpha_channel)) # 融合通道
    return img_new