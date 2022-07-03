<template>
  <div class="app-container" style="overflow:auto">
    <el-row style="box-shadow: 0 2px 4px rgba(0, 0, 0, .12), 0 0 6px rgba(0, 0, 0, .04); padding: 5px;">
      <el-col :span="10" :offset="5">
        <div class="myfont" style="margin:10px">
          选择要检测的目标类别
        </div>
        <el-checkbox v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">全选</el-checkbox>
        <div style="margin: 15px 0;" />
        <el-checkbox-group v-model="checkboxGroup1">
          <el-checkbox-button v-for="label in labels" :key="label" :label="label">{{ label }}</el-checkbox-button>
        </el-checkbox-group>
      </el-col>
      <el-col :span="4">
        <div style="margin-top: 10px;">
          <p class="myfont">预设定四个类别检测框颜色</p>
          <el-color-picker
            v-model="color1"
            show-alpha
            :predefine="predefineColors"
          />
          <el-color-picker
            v-model="color2"
            show-alpha
            :predefine="predefineColors"
          />
          <el-color-picker
            v-model="color3"
            show-alpha
            :predefine="predefineColors"
          />
          <el-color-picker
            v-model="color4"
            show-alpha
            :predefine="predefineColors"
          />
        </div>
      </el-col>
    </el-row>
    <div class="tip" style="margin-top:20px;">
      请上传要分类的遥感图压缩文件
    </div>
    <el-upload
      class="upload-demo"
      drag
      action="#"
      multiple
      accept=".zip"
      :name="name"
      :limit="2"
      :file-list="fileList"
      :show-file-list="true"
      :auto-upload="false"
      :on-change="change"
      :on-error="handleError"
      :before-upload="handleBefore"
      style="text-align: center;"
    >
      <i class="el-icon-upload" />
      <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
      <div slot="tip" class="el-upload__tip">请上传zip压缩文件夹，文件内容为目标提取样本</div>
    </el-upload>
    <el-row style="text-align: center; padding-top:10px;padding-bottom:30px;">
      <el-button type="primary" round :loading="loading" @click="doBatchDiwuclassifacation()">批量目标提取</el-button>
    </el-row>
    <div v-show="resvisible" class="tip">
      检测结果如下
    </div>
    <div v-show="resvisible" class="demo-image__lazy" style="overflow:auto; width: 100%;">
      <el-image v-for="url in urls" :key="url" :src="url" lazy style="text-align: center; width: 230px; height: 230px;" />
    </div>
    <el-row v-show="resvisible" style="text-align: center; padding-top:10px;padding-bottom:30px;">
      <el-button type="primary" round @click="saveResult()">保存结果</el-button>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'
// import * as mammoth from 'mammoth'
import * as JSZip from 'jszip'
import saveAs from 'jszip/vendor/FileSaver.js'
const LabelOptions = ['建筑', '耕地', '林地', '水体']
export default {
  data() {
    return {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      fileList: [],
      name: 'zipfile',
      dialogImageUrl1: '',
      dialogVisible: false,
      resvisible: false,
      loading: false,
      urls: [],
      filenames: [],
      checkAll: true,
      isIndeterminate: true,
      checkboxGroup1: ['建筑', '耕地', '林地', '水体'],
      labels: LabelOptions,
      color1: 'rgba(255, 69, 0, 0.7)',
      color2: 'rgba(30, 144, 255, 0.7)',
      color3: 'rgba(255, 120, 0, 0.7)',
      color4: 'rgba(0, 186, 189, 0.7)',
      predefineColors: [
        'rgba(255, 69, 0, 1)',
        'rgba(255, 140, 0, 1)',
        'rgba(255, 215, 0, 1)',
        'rgba(144, 238, 144, 1)',
        'rgba(0, 206, 209, 1)',
        'rgba(30, 144, 255, 1)',
        'rgba(199, 21, 133, 1)',
        'rgba(255, 69, 0, 0.68)',
        'rgb(255, 120, 0)',
        'rgba(250, 212, 0, 1)',
        'rgba(144, 240, 144, 0.5)',
        'rgba(0, 186, 189, 1)',
        'rgba(31, 147, 255, 0.73)'
      ]
    }
  },
  methods: {
    // 保存纠错结果
    saveResult() {
      // var arr = this.baseurls
      var tempDatas = []
      tempDatas = this.urls
      var tempBlobs = []
      for (var i = 0; i < tempDatas.length; i++) {
        tempBlobs[i] = this.dataURLtoBlob(tempDatas[i])
      }
      if (tempDatas === '') {
        this.$message({
          showClose: true,
          message: '内容为空！',
          type: 'warning'
        })
      } else {
        this.zipclick(tempBlobs)
      }
    },
    zipclick(baseArr) {
      var zip = new JSZip()
      var img = zip.folder('images')
      for (let i = 0; i < baseArr.length; i++) {
        img.file(this.filenames[i], baseArr[i])
      }
      zip.generateAsync({ type: 'blob' })
        .then(function(content) {
          saveAs(content, 'batchres.zip')
        })
    },
    doBatchDiwuclassifacation() {
      var that = this
      that.loading = true
      const formData = new FormData()
      if (that.fileList.length === 0) {
        this.$message({
          showClose: true,
          message: '请先选择要进行分类的图片文件！',
          type: 'warning'
        })
        that.resvisible = false
        return
      } else {
        const selectlabels = []
        if (that.checkboxGroup1.includes('建筑')) {
          selectlabels.push('cls0')
        }
        if (that.checkboxGroup1.includes('耕地')) {
          selectlabels.push('cls1')
        }
        if (that.checkboxGroup1.includes('林地')) {
          selectlabels.push('cls2')
        }
        if (that.checkboxGroup1.includes('水体')) {
          selectlabels.push('cls3')
        }
        formData.append(that.name, that.fileList[0].raw)
        formData.append('CLASS', selectlabels)
        formData.append('COLOR1', that.color1)
        formData.append('COLOR2', that.color2)
        formData.append('COLOR3', that.color3)
        formData.append('COLOR4', that.color4)
        console.log(that.fileList[0].raw)
        // console.log(that.value)
        // 请求后端API服务，请求方法为post，请求体字段为json格式 text
        axios.post('http://10.1.114.93:5000/v1/batchdiwuclassification',
          formData
        ).then((response) => {
          if (response.status === 'ok') {
            console.log('上传成功')
          }
          const urllist = response.data.batchclares
          for (var i = 0; i < urllist.length; i++) {
            urllist[i] = 'data:image/jpeg;base64,' + urllist[i]
          }
          that.urls = urllist
          that.resvisible = true
          that.loading = false
          that.$message({
            showClose: true,
            message: '目标提取完成！',
            type: 'success'
          })
        }).catch((error) => {
          console.log(error)
          that.resvisible = false
          that.loading = false
          that.$message({
            showClose: true,
            message: '请求出现异常！',
            type: 'error'
          })
        })
      }
    },
    handleCheckAllChange(val) {
      this.checkboxGroup1 = val ? LabelOptions : []
      this.isIndeterminate = false
    },
    // base64转blob
    dataURLtoBlob(dataurl) {
      var arr = dataurl.split(',')
      var mime = arr[0].match(/:(.*?);/)[1]
      var bstr = atob(arr[1])
      var n = bstr.length
      var u8arr = new Uint8Array(n)
      while (n--) {
        u8arr[n] = bstr.charCodeAt(n)
      }
      return new Blob([u8arr], { type: mime })
    },
    // ArrayBuffer转为base64字符串
    arrayBufferToBase64(buffer) {
      // 第一步，将ArrayBuffer转为二进制字符串
      var binary = ''
      var bytes = new Uint8Array(buffer)
      var len = bytes.byteLength
      for (var i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i])
      }
      // 将二进制字符串转为base64字符串
      return window.btoa(binary)
    },
    change(file, fileList) {
    // 将每次图片数组变化的时候，实时的进行监听，更改数组里面的图片数据
      if (fileList.length > 0) {
        this.fileList = [fileList[fileList.length - 1]]
        this.dialogImageUrl1 = URL.createObjectURL(file.raw)
      }
    },
    handleBefore(file) {
      var FileExt = file.name.replace(/.+\./, '')
      if (['zip', 'rar', 'gz', '.apk'].indexOf(FileExt.toLowerCase()) === -1) {
        this.message = '文件格式有误，请重新上传'
        return false
      }
    }
  }
}
</script>

<style scoped>
  .tip {
    font-family: 宋体;
  font-size: 18px;
	font-weight: bold;
	margin-bottom: 20px;
  margin-bottom: 10px;
  text-align: center;
  }
</style>

<style>
  .avatar-uploader .el-upload {
    border: 1px dashed #d9d9d9;
    border-radius: 6px;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }
  .avatar-uploader .el-upload:hover {
    border-color: #409EFF;
  }
  .avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 230x;
    height: 230px;
    line-height: 230px;
    text-align: center;
  }
  .avatar {
    width: 230px;
    height: 230px;
    display: block;
  }
</style>

<style>
.el-upload--picture-card {
    background-color: #fbfdff;
    border: 1px dashed #c0ccda;
    border-radius: 6px;
    -webkit-box-sizing: border-box;
    box-sizing: border-box;
    width: 230px;
    height: 230px;
    line-height: 146px;
    vertical-align: top;
}
</style>
