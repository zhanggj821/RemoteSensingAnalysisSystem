import zipfile
import datetime
import base64
import sys
import re
sys.path.append('/home/guangjun/PaddleRS')
import os
import numpy as np
import imageio
import cv2
from paddlers.utils.logging import debug
from skimage.io import imread, imsave
import numpy as np
from flask_cors import CORS, cross_origin
from flask import Flask, render_template, request, make_response
import paddlers as pdrs
from paddlers import transforms as T
from flask_paddlers.myutils.crop import crop_img, recons_prob_map, quantize
from flask_paddlers.myutils.visualize import visualize_detection
from flask_paddlers.myutils.add_channel import add_alpha_channel


app = Flask(__name__)
CORS(app, supports_credentials=True)

def parsecolor(color):
    partten = r'\d+\.\d+|\d+'
    res = re.findall(partten, color)
    lut = [0,0,0,0]
    lut[0] = int(res[2])
    lut[1] = int(res[1])
    lut[2] = int(res[0])
    lut[3] = int(float(res[3])*255)
    return lut


@app.route('/v1/changedetection', methods=['GET', 'POST'])
def changedectection():
    if request.method == 'POST':
        sensebefor = request.files['sensingbefor']
        senseafter = request.files['sensingafter']
        step = int(request.form.get('STEP'))
        confidence = float(request.form.get('CONFIDENCE'))
        color = request.form.get('COLOR')
        print(color)
        print(type(color))
        color = parsecolor(color)
        
        sensebefor = sensebefor.read()
        senseafter = senseafter.read()
        
        
        sensebefor = cv2.imdecode(np.frombuffer(sensebefor, np.uint8), cv2.IMREAD_COLOR)
        senseafter = cv2.imdecode(np.frombuffer(senseafter, np.uint8), cv2.IMREAD_COLOR)
        
        
        
        predictor = pdrs.deploy.Predictor('/home/guangjun/PaddleRS/flask_paddlers/infer_model/inference_changedetection', use_gpu=True)
        trans = T.Compose([
        T.Normalize() ])
        imgs = [sensebefor, senseafter]
        patches = crop_img(imgs, (1024, 1024), 256, step)
        patch_res = []
        for t in patches:
            result = predictor.predict(img_file=(t[0], t[1]), transforms=trans)
            patch_res.append(result[0]['score_map'][:,:,1])
        prob = recons_prob_map(patch_res, (1024,1024), 256, step)
        out = (prob>confidence).astype('uint8')       # 1024*1024
        
        def get_lut():
            lut = np.zeros((2,4), dtype=np.uint8)
            lut[0] = [0, 0, 0, 0]
            lut[1] = color
            return lut
        
        lut = get_lut()
        
        out = lut[out]
        
        root = '/home/guangjun/PaddleRS/flask_paddlers/storage/changedetection'
        savepath  = os.path.join(root, 'change_rgba.png')
        cv2.imwrite(savepath,  out)
        
        out_rgba = cv2.imread(savepath, cv2.IMREAD_UNCHANGED)
        senseafter_rgba = add_alpha_channel(senseafter)
        
        alpha = out_rgba[:,:,3] / 255.0
        
        for c in range(0,3):
            senseafter_rgba[:, :, c] = (((1-alpha)*senseafter_rgba[:,:,c]) + (alpha*out_rgba[:,:,c]))
        
        savepath  = os.path.join(root, 'change_rgba_merge.png')
        cv2.imwrite(savepath, senseafter_rgba)
        
        with open(savepath, 'rb') as f:
            img_byte = f.read()     #二进制编码
            img_b64 = base64.b64encode(img_byte)    #img_b64是字节类型变量，b64.encode()对字节类型变量进行b64编码，bytes->bytes
            img_res = img_b64.decode('utf-8')      #img_str是字符串类型变量，decode()对字节类型变量进行解码，bytes->str
        
        mergelist = []
        mergedir = os.path.join(root, 'giflist')
        if not os.path.exists(mergedir):
            os.makedirs(mergedir)
        out =  cv2.imread(savepath)
        for i, rate in enumerate(np.arange(0, 1, 0.1)):
            mergeimg = cv2.addWeighted(sensebefor,alpha=(1-rate),src2=out,beta=rate,gamma=1)
            savepath  = os.path.join(mergedir, 'merge_{}.jpg'.format(i))
            cv2.imwrite(savepath, mergeimg)
            with open(savepath, 'rb') as f:
                img_byte = f.read()     #二进制编码
                img_b64 = base64.b64encode(img_byte)    #img_b64是字节类型变量，b64.encode()对字节类型变量进行b64编码，bytes->bytes
                img_merge = img_b64.decode('utf-8')      #img_str是字符串类型变量，decode()对字节类型变量进行解码，bytes->str
            
            mergelist.append(img_merge)
            
        gif = []
        imgs =  os.listdir(mergedir)
        imgs.sort()
        for im in imgs:
            print(im)
            gif.append(imageio.imread(os.path.join(mergedir, im)))
        imageio.mimsave(os.path.join(root, 'merge.gif'), gif, fps=2)
        
        with open(os.path.join(root, 'merge.gif'), 'rb') as f:
            gif_byte = f.read()
            gif_b64 = base64.b64encode(gif_byte)
            gif_res = gif_b64.decode('utf-8')
         
        result = {'changeres':img_res, 'mergelist':mergelist, 'gif':gif_res}
        
        res = make_response(result)
        return res
    
    

@app.route('/v1/objectdetection', methods=['GET', 'POST'])
def objectdetection():
    if request.method == 'POST':
        img = request.files['senseimage']
        CLASS = request.form.get('CLASS')
        CLASS = CLASS.split(',')
        CONFIDENCE = float(request.form.get('CONFIDENCE'))
        color1 =  request.form.get('COLOR1')
        color2 =  request.form.get('COLOR2')
        color3 =  request.form.get('COLOR3')
        color4 =  request.form.get('COLOR4')
        color1 = parsecolor(color1)
        color2 = parsecolor(color2)
        color3 = parsecolor(color3)
        color4 = parsecolor(color4)
        
        print(CLASS)
        print(CONFIDENCE)
        print(type(img))
        
        img = img.read()
        print(type(img))
        
        img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
        print(type(img))
        
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
        
        result = predictor.predict(img_file=img, transforms=trans)
        
        vis = visualize_detection(
                        np.array(img), result, CLASS,
                        color=np.asarray([color1, color2, color3, color4], dtype=np.uint8), 
                        threshold=CONFIDENCE, save_dir=None
                    )
        
        root = '/home/guangjun/PaddleRS/flask_paddlers/storage/objectdetection'
        savepath = os.path.join(root, 'detection.jpg')
        cv2.imwrite(savepath, vis)
        
        with open(savepath, 'rb') as f:
            img_stream = f.read()
            base64_data = base64.b64encode(img_stream).decode('utf-8') # bytes--->str  (remove `b`)
        
        # img_stream = cv2.imread('detection.jpg')
        # print(type(img_stream))    
        # success,encoded_image = cv2.imencode(".jpg", img_stream)
        # print(type(encoded_image))
        # img_stream = encoded_image.tostring()
        # print(type(img_stream))
        
        img_stream = {"detecres" : base64_data }
        
        response = make_response(img_stream)
        # response.data = img_stream
        # response.headers['Content-Type'] = 'image/jpg' #返回的内容类型必须修改
        return response
    

    
    
@app.route('/v1/batchobjectdetection', methods=['GET', 'POST'])
def batchobjectdedtection():
    if request.method == 'POST':
        file = request.files['zipfile']
        CLASS = request.form.get('CLASS')
        CLASS = CLASS.split(',')
        CONFIDENCE = float(request.form.get('CONFIDENCE'))
        color1 =  request.form.get('COLOR1')
        color2 =  request.form.get('COLOR2')
        color3 =  request.form.get('COLOR3')
        color4 =  request.form.get('COLOR4')
        color1 = parsecolor(color1)
        color2 = parsecolor(color2)
        color3 = parsecolor(color3)
        color4 = parsecolor(color4)
        fileName = file.filename
        if str(fileName).split('.')[1] != 'zip':
            return {'code': '200', 'msg': '文件后缀名出现错误'}
        startNow = datetime.datetime.now()
        zip_file = zipfile.ZipFile(file)
        unzipdir = "/home/guangjun/PaddleRS/flask_paddlers/storage/unzipdir/objectdetection" # 解压后名称
        for names in zip_file.namelist():  #解压 
            zip_file.extract(names, unzipdir) 
        zip_file.close()
        endNow = datetime.datetime.now()
        print(endNow - startNow)
        batchroot = os.path.join(unzipdir, fileName.split('.')[0])
        filelist = os.listdir(batchroot)
        
        imgs = []
        for filename in filelist:
            path = os.path.join(unzipdir, fileName.split('.')[0], filename)
            print(path)
            img = cv2.imread(path)
            imgs.append(img)
        
            
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
        results = predictor.predict(img_file=imgs, transforms=trans)
        
        reslist = []
        
        out_dir = os.path.join(unzipdir, fileName.split('.')[0]+'_res')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
        for index, (im, name) in enumerate(zip(imgs, filelist)):
            vis = visualize_detection(
                np.array(im), results[index], CLASS,    
                color=np.asarray([color1, color2, color3, color4], dtype=np.uint8), 
                threshold=CONFIDENCE, save_dir=None
            )
            savepath = os.path.join(out_dir, name)
            cv2.imwrite(savepath, vis)  
            with open(savepath, 'rb') as f:
                img_byte = f.read()     #二进制编码
                img_b64 = base64.b64encode(img_byte)    #img_b64是字节类型变量，b64.encode()对字节类型变量进行b64编码，bytes->bytes
                img_res = img_b64.decode('utf-8')      #img_str是字符串类型变量，decode()对字节类型变量进行解码，bytes->str remove b''
                reslist.append(img_res)
        
        result = {'batchdetecres': reslist, 'filelist':filelist}
        res = make_response(result)
        return res


@app.route('/v1/diwuclassification', methods=['GET', 'POST'])
def objectclassification():
    if request.method == 'POST':
        img = request.files['senseimage']
        CLASS = request.form.get('CLASS')
        CLASS = CLASS.split(',')
        color1 =  request.form.get('COLOR1')
        color2 =  request.form.get('COLOR2')
        color3 =  request.form.get('COLOR3')
        color4 =  request.form.get('COLOR4')
        color1 = parsecolor(color1)
        color2 = parsecolor(color2)
        color3 = parsecolor(color3)
        color4 = parsecolor(color4)
        
        img = img.read()
        
        img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
        
        predictor = pdrs.deploy.Predictor('/home/guangjun/PaddleRS/flask_paddlers/infer_model/inference_classification', use_gpu=True)
        trans = T.Compose([
            T.Resize(target_size=256),
            # 验证阶段与训练阶段的数据归一化方式必须相同
            T.Normalize(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        root = '/home/guangjun/PaddleRS/flask_paddlers/storage/diwuclassification' 
        
        def get_lut(SelectLabels):
            lut = np.zeros((5,4), dtype=np.uint8)
            lut[0] = [int('cls0' in SelectLabels) * i for i in color1]
            lut[1] = [int('cls1' in SelectLabels) * i for i in color2]
            lut[2] = [int('cls2' in SelectLabels) * i for i in color3]
            lut[3] = [int('cls3' in SelectLabels) * i for i in color4]
            lut[4] = [0, 0, 0, 0]
            return lut
        
        def showimg(im, path, lut=None):
            if im.ndim == 3:
                im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            im = lut[im]
            cv2.imwrite(path, im)

        result = predictor.predict(img_file=img, transforms=trans)
        pred_map = result['label_map']
        savepath = os.path.join(root, 'cls_rgba.png')
        showimg(pred_map, savepath ,lut = get_lut(CLASS))
        
        cls_rgba = cv2.imread(savepath, cv2.IMREAD_UNCHANGED)
        img_rgba = add_alpha_channel(img)
        
        alpha = cls_rgba[:,:,3] / 255.0
        
        for c in range(0,3):
            img_rgba[:, :, c] = (((1-alpha)*img_rgba[:,:,c]) + (alpha*cls_rgba[:,:,c]))
        
        savepath = os.path.join(root, 'cls_rgba_merge.jpg')
        cv2.imwrite(savepath, img_rgba)
        
        
        with open(savepath, 'rb') as f:
            img_byte = f.read()     #二进制编码
            img_b64 = base64.b64encode(img_byte)    #img_b64是字节类型变量，b64.encode()对字节类型变量进行b64编码，bytes->bytes
            img_res = img_b64.decode('utf-8')      #img_str是字符串类型变量，decode()对字节类型变量进行解码，bytes->str remove b''
        
        result = {'clares': img_res}
        
        res = make_response(result)
        # response.headers['Content-Type'] = 'image/jpg' #返回的内容类型必须修改
        return res
    
    

@app.route('/v1/batchdiwuclassification', methods=['GET', 'POST'])
def batchdiwuclassification():
    if request.method == 'POST':
        file = request.files['zipfile']
        CLASS = request.form.get('CLASS')
        CLASS = CLASS.split(',')
        color1 =  request.form.get('COLOR1')
        color2 =  request.form.get('COLOR2')
        color3 =  request.form.get('COLOR3')
        color4 =  request.form.get('COLOR4')
        color1 = parsecolor(color1)
        color2 = parsecolor(color2)
        color3 = parsecolor(color3)
        color4 = parsecolor(color4)
        fileName = file.filename
        if str(fileName).split('.')[1] != 'zip':
            return {'code': '200', 'msg': '文件后缀名出现错误'}
        startNow = datetime.datetime.now()
        zip_file = zipfile.ZipFile(file)
        unzipdir = "/home/guangjun/PaddleRS/flask_paddlers/storage/unzipdir/diwuclassification" # 解压后名称
        for names in zip_file.namelist():  #解压 
            zip_file.extract(names, unzipdir) 
        zip_file.close()
        endNow = datetime.datetime.now()
        print(endNow - startNow)
        batchroot = os.path.join(unzipdir, fileName.split('.')[0])
        filelist = os.listdir(batchroot)
        
        imgs = []
        for filename in filelist:
            path = os.path.join(unzipdir, fileName.split('.')[0], filename)
            print(path)
            img = cv2.imread(path)
            imgs.append(img)
        
        predictor = pdrs.deploy.Predictor('/home/guangjun/PaddleRS/flask_paddlers/infer_model/inference_classification', use_gpu=True)
        trans = T.Compose([
            T.Resize(target_size=256),
            # 验证阶段与训练阶段的数据归一化方式必须相同
            T.Normalize(
                mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])
        
        def get_lut(SelectLabels):
            lut = np.zeros((5,4), dtype=np.uint8)
            lut[0] = [int('cls0' in SelectLabels) * i for i in color1]
            lut[1] = [int('cls1' in SelectLabels) * i for i in color2]
            lut[2] = [int('cls2' in SelectLabels) * i for i in color3]
            lut[3] = [int('cls3' in SelectLabels) * i for i in color4]
            lut[4] = [0, 0, 0, 0]
            return lut
        
        def saveimg(im, path, lut=None):
            if im.ndim == 3:
                im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
            im = lut[im]
            cv2.imwrite(path, im)
            
        
        results = predictor.predict(img_file=imgs, transforms=trans)
        
        reslist = []
        
        out_dir = os.path.join(unzipdir, fileName.split('.')[0]+'_res')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
        out_dir_merge_rgba = os.path.join(out_dir, 'merge_rgba')
        if not os.path.exists(out_dir_merge_rgba):
            os.makedirs(out_dir_merge_rgba)
        
        for index, (result, filename) in enumerate(zip(results, filelist)): 
            pred_map =  result['label_map']
            
            if(filename.endswith('jpg')):
                filename = list(filename)
                i = filename.index('.')
                filename[i+1:] = 'png'
                filename = ''.join(filename)
            
            savepath = os.path.join(out_dir, filename)
            saveimg(pred_map, savepath,lut=get_lut(CLASS))
            
            cls_rgba = cv2.imread(savepath, cv2.IMREAD_UNCHANGED)
            img_rgba = add_alpha_channel(imgs[index])
            
            alpha = cls_rgba[:,:,3] / 255.0
            
            for c in range(0,3):
                img_rgba[:, :, c] = (((1-alpha)*img_rgba[:,:,c]) + (alpha*cls_rgba[:,:,c]))
        
            

            savepath = os.path.join(out_dir_merge_rgba,filename)
            cv2.imwrite(savepath, img_rgba)
            
            with open(savepath, 'rb') as f:
                img_byte = f.read()     #二进制编码
                img_b64 = base64.b64encode(img_byte)    #img_b64是字节类型变量，b64.encode()对字节类型变量进行b64编码，bytes->bytes
                img_res = img_b64.decode('utf-8')      #img_str是字符串类型变量，decode()对字节类型变量进行解码，bytes->str remove b''
                reslist.append(img_res)
        
        result = {'batchclares': reslist, 'filelist':filelist}
        res = make_response(result)
        return res    

    

@app.route('/v1/objectextraction', methods=['GET', 'POST'])
def objectextraction():
    if request.method == 'POST':
        img = request.files['senseimage']
        CONFIDENCE = float(request.form.get('CONFIDENCE'))
        color =  request.form.get('COLOR')
        color = parsecolor(color)
        
        img = img.read()
        
        img = cv2.imdecode(np.frombuffer(img, np.uint8), cv2.IMREAD_COLOR)
        
        predictor = pdrs.deploy.Predictor('/home/guangjun/PaddleRS/flask_paddlers/infer_model/inference_extraction', use_gpu=True)
        trans = T.Compose([
            T.Resize(target_size=1488),
            # 验证阶段与训练阶段的数据归一化方式必须相同
            T.Normalize(
            mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])

        result = predictor.predict(img_file=img, transforms=trans)
        label_map = result['score_map'][:,:,-1]
        label_map = (label_map > CONFIDENCE).astype('uint8')
        
        def get_lut():
            lut = np.zeros((2,4), dtype=np.uint8)
            lut[0] = [0, 0, 0, 0]
            lut[1] = color
            return lut
        
        lut = get_lut()
        
        out = lut[label_map]
        
        root = '/home/guangjun/PaddleRS/flask_paddlers/storage/objectextraction'
        savepath = os.path.join(root, 'extraction_rgba.png')
        cv2.imwrite(savepath, out)
        
        extrac_rgba = cv2.imread(savepath, cv2.IMREAD_UNCHANGED)
        img_rgba = add_alpha_channel(img)
        
        alpha = extrac_rgba[:,:,3] / 255.0
        
        for c in range(0,3):
            img_rgba[:, :, c] = (((1-alpha)*img_rgba[:,:,c]) + (alpha*extrac_rgba[:,:,c]))
        
        savepath  = os.path.join(root, 'extrac_rgba_merge.png')
        cv2.imwrite(savepath, img_rgba)
        
        with open(savepath, 'rb') as f:
            img_byte = f.read()     #二进制编码
            img_b64 = base64.b64encode(img_byte)    #img_b64是字节类型变量，b64.encode()对字节类型变量进行b64编码，bytes->bytes
            img_res = img_b64.decode('utf-8')      #img_str是字符串类型变量，decode()对字节类型变量进行解码，bytes->str remove b''
  
        result = {'extracres':img_res}
        res = make_response(result)
        return res
    
@app.route('/v1/batchobjectextraction', methods=['GET', 'POST'])
def batchobjectextraction():
    if request.method == 'POST':
        file = request.files['zipfile']
        CONFIDENCE = float(request.form.get('CONFIDENCE'))
        color =  request.form.get('COLOR')
        color = parsecolor(color)
        
        fileName = file.filename
        if str(fileName).split('.')[1] != 'zip':
            return {'code': '200', 'msg': '文件后缀名出现错误'}
        startNow = datetime.datetime.now()
        zip_file = zipfile.ZipFile(file)
        unzipdir = "/home/guangjun/PaddleRS/flask_paddlers/storage/unzipdir/objectextraction" # 解压后名称
        for names in zip_file.namelist():  #解压 
            zip_file.extract(names, unzipdir) 
        zip_file.close()
        endNow = datetime.datetime.now()
        print(endNow - startNow)
        batchroot = os.path.join(unzipdir, fileName.split('.')[0])
        filelist = os.listdir(batchroot)
        
        def get_lut():
            lut = np.zeros((2,4), dtype=np.uint8)
            lut[0] = [0, 0, 0, 0]
            lut[1] = color
            return lut
        
        lut = get_lut()
        
        imgs = []
        for filename in filelist:
            path = os.path.join(unzipdir, fileName.split('.')[0], filename)
            print(path)
            img = cv2.imread(path)
            imgs.append(img)
        
        predictor = pdrs.deploy.Predictor('/home/guangjun/PaddleRS/flask_paddlers/infer_model/inference_extraction', use_gpu=True)
        trans = T.Compose([
            T.Resize(target_size=1488),
            # 验证阶段与训练阶段的数据归一化方式必须相同
            T.Normalize(
                mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
        ])
        results = predictor.predict(img_file=imgs, transforms=trans)
        
        reslist = []
        
        out_dir = os.path.join(unzipdir, fileName.split('.')[0]+'_res')
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
            
        out_dir_merge_rgba = os.path.join(out_dir, 'merge_rgba')
        if not os.path.exists(out_dir_merge_rgba):
            os.makedirs(out_dir_merge_rgba)
        
        for index, (result, filename) in enumerate(zip(results, filelist)):
            pred_map =  result['score_map'][:,:,-1]
            pred_map = (pred_map > CONFIDENCE).astype('uint8')
            pred_map = lut[pred_map]
            
            if(filename.endswith('png') is False):
                filename = list(filename)
                i = filename.index('.')
                filename[i+1:] = 'png'
                filename = ''.join(filename)
                
            savepath = os.path.join(out_dir, filename)
            cv2.imwrite(savepath, pred_map)
            
            extrac_rgba = cv2.imread(savepath, cv2.IMREAD_UNCHANGED)
            img_rgba = add_alpha_channel(imgs[index])
            
            alpha = extrac_rgba[:,:,3] / 255.0
            
            for c in range(0,3):
                img_rgba[:, :, c] = (((1-alpha)*img_rgba[:,:,c]) + (alpha*extrac_rgba[:,:,c]))
            
            savepath = os.path.join(out_dir_merge_rgba,filename)
            cv2.imwrite(savepath, img_rgba)            
            
            with open(savepath, 'rb') as f:
                img_byte = f.read()     #二进制编码
                img_b64 = base64.b64encode(img_byte)    #img_b64是字节类型变量，b64.encode()对字节类型变量进行b64编码，bytes->bytes
                img_res = img_b64.decode('utf-8')      #img_str是字符串类型变量，decode()对字节类型变量进行解码，bytes->str remove b''
                reslist.append(img_res)
        
        
        result = {'batchextracres': reslist, 'filelist':filelist}
        res = make_response(result)
        return res
    

if __name__ == '__main__':
	app.run(host="0.0.0.0", debug=True)
    