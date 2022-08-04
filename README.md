# RemoteSensingAnalysisSystem
## 一. 项目说明
1. 遥感图像解析是一项CV基础任务，包括目标检测、语义分割，其输入是一副或一组遥感图像输出是对遥感图像解析的结果, 例如对其进行变化检测、目标检测、地物分类、道路提取等基础功能。我们的**遥感图像解析系统(RSAS)**是一项基于百度深度学习框架PaddlePaddle的封装产品PaddleRS训练模型，从而帮助用户更好地使用以上四个功能。
2. 该项目技术栈：后端：PaddleRS + Flask; 前端：Vue2 + Element UI
3. web端主要功能：用户可以根据具体需求上传遥感图像完成相应的解析，此过程中用户可以自定义模型参数以及分析结果呈现的样式。此外我们还提供批处理功能，用户只需将要检测的图片打包上传即可。
4. 模型训练部分不再展开，具体参考各个模型baseline：[变化检测](https://aistudio.baidu.com/aistudio/projectdetail/3684588?ticket=f89b1634de0e4e60a203d82e39558a9b&alertTip=&qq-pf-to=pcqq.group)、 [目标检测](https://aistudio.baidu.com/aistudio/projectdetail/3792609)、[道路提取](https://aistudio.baidu.com/aistudio/projectdetail/3792610)、[地物分类](https://aistudio.baidu.com/aistudio/projectdetail/3792606)。
5. 前端脚手架Github地址：https://github.com/PanJiaChen/vue-admin-template

## 二. 项目环境配置
### 1. 后端环境配置：
首先需要下载安装Python包管理器Anaconda：https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/
访问镜像下载网站，根据自己电脑系统（win64或Linux等）选择合适的版本，建议选择较新的版本。

// 配置清华源镜像加速
 conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
 conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
 conda config --set show_channel_urls yes

//创建新环境，环境名为csc，python版本为3.7
conda create -n paddle python=3.7

// 进入刚才创建的虚拟环境paddle，注意后续环境配置操作都将在该环境中进行配置！！！
conda activate paddle

// 安装paddle，建议安装GPU版本性能更优。简化配置的话也可以下载CPU版本
// paddle官网下载地址（根据型号等进行选择）：
https://www.paddlepaddle.org.cn/install/quick?docurl=/documentation/docs/zh/install/pip/linux-pip.html

// 若安装gpu版本需要先配置cuda和cudnn，参考教程：
https://aistudio.baidu.com/aistudio/projectdetail/696822?channelType=0&channel=0
本项目是安装在linux系统

// 安装PaddleRS 参考此链接 https://github.com/PaddleCV-SIG/PaddleRS
```
git clone https://github.com/PaddleCV-SIG/PaddleRS
cd PaddleRS
git checkout develop
pip install -r requirements.txt
python setup.py install
```

//安装后端框架Flask
```
pip install Flask
```
#### 1.1 后端代码结构

这部分将展示后端的文件结构全貌。文件树如下：

```
    
├── backend  
│     ├── infer_model    # 用于预测的静态模型
│     ├── myutils        # 各种实用程序文件
│     ├── storage        # 保存前端上传的文件与结果文件
│     ├── test           # 相关测试代码
│     ├── app.py         # 主程序文件
```

模型链接: https://pan.baidu.com/s/1qPju7IhLS_ZYWsBP0ac9Fw?pwd=fb4h 提取码: fb4h 下载完成后放在infer_model文件夹下即可

修改app.py中的sys.path.append路径，以及projectroot 改为自己的项目路径

启动后端服务
```
cd backend
python app.py
```
// ps:看到“Application startup complete”和“Uvicorn ruuning on http:127.0.0.1:8000”代表后端API项目启动成功


### 2. 前端环境配置
建议下载个前端IDE便于调试，建议使用VS Code，在VS Code插件市场下载vue和eslint插件。

安装node.js，后续需要使用到npm管理包：https://nodejs.org/en/download/

参考：

Windows：https://m.php.cn/article/483528.html

Linux: https://blog.csdn.net/qq_41974199/article/details/119328353


// 通过cd命令进行项目frontend文件夹，安装项目依赖
```
cd fronted
npm install
```
#### 2.1 前端代码结构

这部分将展示前端的文件结构全貌。文件树如下：

```
├── build                      # build config files
├── mock                       # mock data
├── plop-templates             # basic template
├── public                     # pure static assets (directly copied)
│   │── favicon.ico            # favicon
│   └── index.html             # index.html template
├── src                        # main source code
│   ├── api                    # api service
│   ├── assets                 # module assets like fonts,images (processed by webpack)
│   ├── components             # global components
│   ├── directive              # global directive
│   ├── filters                # global filter
│   ├── icons                  # svg icons
│   ├── lang                   # i18n language
│   ├── layout                 # global layout
│   ├── router                 # router
│   ├── store                  # store
│   ├── styles                 # global css
│   ├── utils                  # global utils
│   ├── vendor                 # vendor
│   ├── views                  # views (主要代码在这个文件夹下，每个文件夹表示一个组件(页面))
│   ├── App.vue                # main app component
│   ├── main.js                # app entry file
│   └── permission.js          # permission authentication
├── tests                      # tests
├── .env.xxx                   # env variable configuration
├── .eslintrc.js               # eslint config
├── .babelrc                   # babel config
├── .travis.yml                # automated CI configuration
├── vue.config.js              # vue-cli config
├── postcss.config.js          # postcss config
└── package.json               # package.json
```


启动前端项目
```
npm run dev
```
// ps:看到App running at:Local: http://localhost:9528代表项目启动成功
此时访问http://localhost:9528即可进入系统

// 注意要完整访问的话，前端和后端项目都要启动哦！

testgit