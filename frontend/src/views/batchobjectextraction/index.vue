<template>
  <div class="app-container" style="overflow: auto;">
    <el-row style="box-shadow: 0 2px 4px rgba(0, 0, 0, .12), 0 0 6px rgba(0, 0, 0, .04); padding: 5px;">
      <el-col :span="4" :offset="8">
        <div style="margin-top: 10px;">
          <p class="myfont">预设定提取颜色</p>
          <el-color-picker
            v-model="color"
            show-alpha
            :predefine="predefineColors"
          />
        </div>
      </el-col>
      <el-col :span="6" :offset="2">
        <div class="block" style="margin-top: 20px;">
          <span class="myfont" style="text-align:center">置信度阈值</span>
          <el-slider v-model="confidence" :format-tooltip="formatTooltip" :min="0.1" :max="0.9" :step="0.1" show-input />
        </div>
      </el-col>
    </el-row>
    <div class="tip" style="margin-top:20px">
      请上传要提取的遥感图压缩文件
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
      <el-button type="primary" round :loading="loading" @click="doBatchObjectExtraction()">批量目标提取</el-button>
    </el-row>
    <div v-show="resvisible" class="tip">
      检测结果如下
    </div>
    <div v-show="resvisible" class="demo-image__lazy" style="width: 100%; text-align: center;">
      <el-image v-for="url in urls" :key="url" :src="url" :preview-src-list="[url]" lazy style="text-align: center; width: 230px; height: 230px; margin: 10px;" />
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
      color: 'rgba(255, 69, 0, 1)',
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
      ],
      confidence: 0.5
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
    doBatchObjectExtraction() {
      var that = this
      that.loading = true
      that.resvisible = false
      const formData = new FormData()
      if (that.fileList.length === 0) {
        this.$message({
          showClose: true,
          message: '请先选择要进行提取的图片以及目标类别！',
          type: 'warning'
        })
        that.resvisible = false
        return
      } else {
        formData.append(that.name, that.fileList[0].raw)
        formData.append('CONFIDENCE', that.confidence)
        formData.append('COLOR', that.color)
        // formData.append('CLASS', that.value)
        console.log(that.fileList[0].raw)
        // console.log(that.value)
        // 请求后端API服务，请求方法为post，请求体字段为json格式 text
        axios.post('http://10.1.114.93:5000/v1/batchobjectextraction',
          formData
        ).then((response) => {
          if (response.status === 'ok') {
            console.log('上传成功')
          }
          const urllist = response.data.batchextracres
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
    formatTooltip(val) {
      return val
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
