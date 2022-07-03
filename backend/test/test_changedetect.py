from cProfile import label
from cgi import print_arguments
import sys
sys.path.append('/home/guangjun/PaddleRS')
import imp
import paddle
import paddlers as pdrs
from paddlers import transforms as T
import numpy as np
import os.path as osp
from skimage.io import imread, imsave

from flask_paddlers.myutils.crop import crop_img, recons_prob_map, quantize


predictor = pdrs.deploy.Predictor('/home/guangjun/PaddleRS/flask_paddlers/inference_changedetection', use_gpu=True)


image_befor_path_1 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/changedetection/A_train_4_0_3.png'
image_after_path_1 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/changedetection/B_train_4_0_3.png'
image_befor_path_2 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/changedetection/A_train_4_0_3.png'
image_after_path_2 = '/home/guangjun/PaddleRS/flask_paddlers/testimgs/changedetection/B_train_4_0_3.png'


trans = T.Compose([
    T.Normalize()
])

im_befor_1 = imread(image_befor_path_1)
im_after_1 = imread(image_after_path_1)

im_befor_2 = imread(image_befor_path_1)
im_after_2 = imread(image_after_path_1)

imgs = []
imgs.append((im_befor_1, im_after_1))
imgs.append((im_befor_2, im_after_2))


imgs = (im_befor_1, im_after_1)

result = predictor.predict(img_file=imgs, transforms=trans)

print(len(result))

# for index, pair in enumerate(imgs):
#     patches = crop_img(pair, (1024, 1024), 256, 64)    
#     patch_res = []
#     for t in patches:
#         result = predictor.predict(img_file=(t[0], t[1]))
#         patch_res.append(result[0]['score_map'][:,:,1])
#     prob = recons_prob_map(patch_res, (1024,1024), 256, 64)
#     out = quantize(prob>0.5)
#     imsave('../testimgs/changedetection/infer_change_'+ str(index) +'.png', out, check_contrast=False)
#     pass



# patches = crop_img(imgs, (1024, 1024), 256, 64)
# print(len(patches))
# print(len(patches[0]))


# patch_res = []
# for t in patches:
#     print('-----')
#     result = predictor.predict(img_file=(t[0], t[1]))
#     patch_res.append(result[0]['score_map'][:,:,1])
# prob = recons_prob_map(patch_res, (1024,1024), 256, 64)
# out = quantize(prob>0.5)
# # print(out.shape)
# imsave('../testimgs/change_18.png', out, check_contrast=False)




# result = predictor.predict(img_file=(image_befor_path, image_after_path))
# score_map = result[0]['score_map'][:, :, -1]
# label_map = result[0]['label_map']
# # imsave('./change_403_infer.png', quantize(score_map>0.5), check_contrast=False)
# imsave('../testimgs/change_403_infer_label.png', label_map, check_contrast=False)


# im_befor = imread(image_befor_path)
# im_after = imread(image_after_path)
# imgs = [im_befor, im_after]
# patches = crop_img(imgs, (1024, 1024), 256, 64)
# print(len(patches))
# print(len(patches[0]))


# patch_res = []
# for t in patches:
#     print('-----')
#     result = predictor.predict(img_file=(t[0], t[1]))
#     patch_res.append(result[0]['score_map'][:,:,1])
# prob = recons_prob_map(patch_res, (1024,1024), 256, 64)
# out = quantize(prob>0.5)
# # print(out.shape)
# imsave('./change_5.png', out, check_contrast=False)



##############################################################
# img_file = (image_befor_path, image_after_path)
# if isinstance(img_file, (str, np.ndarray, tuple)):
#     # images = [img_file]
#     print(type(img_file))
#     images = [img_file]
#     print(type(images))
# else:
#     img_file = img_file
#     print("no")

# pred = paddle.zeros
# for imgb, imga in patch:


# result = predictor.predict(img_file=img_file)
# label_map = result[0]['label_map']
# score_map = result[0]['score_map']
# print(type(label_map)) 
# print(type(score_map))
# print(label_map.shape)
# print(score_map.shape)
# print(label_map)
# print(score_map)


# score = np.sum(score_map, axis=2)
# print(score)
# mask = np.unique(label_map)
# tmp = {}
# for v in mask:
#     tmp[v] = np.sum(label_map == v)
# print(tmp)

# for i in range(256):
#     for j in range(256):
#         if(label_map[i, j] == 1):
#             print(score_map[i,j,:])





