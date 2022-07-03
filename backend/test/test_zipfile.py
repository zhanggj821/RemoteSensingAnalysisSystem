import zipfile
import os
import cv2
import paddlers as pdrs
from paddlers import transforms as T

file = '/home/guangjun/PaddleRS/flask_paddlers/test/batch.zip'
fileName = 'batch.zip'
zip_file = zipfile.ZipFile(file)
unzipdir = "/home/guangjun/PaddleRS/flask_paddlers/unzipdir/objectdetection" # 解压后名称
for names in zip_file.namelist():  #解压 
    zip_file.extract(names, unzipdir) 
zip_file.close()


batchroot = os.path.join(unzipdir, fileName.split('.')[0])
filelist = os.listdir(batchroot)

imgs = []
for filename in filelist:
    path = os.path.join(unzipdir, fileName.split('.')[0], filename)
    print(path)
    img = cv2.imread(path)
    imgs.append(img)
print(len(imgs))
print(imgs[0].shape)
    
predictor = pdrs.deploy.Predictor('/home/guangjun/PaddleRS/flask_paddlers/inference_model_detection_ppyolo/all', use_gpu=True)
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
result = predictor.predict(img_file=imgs, transforms=trans)
print(len(result))