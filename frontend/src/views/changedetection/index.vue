<template>
  <div class="app-container" style="overflow:auto;">
    <el-row style="box-shadow: 0 2px 4px rgba(0, 0, 0, .12), 0 0 6px rgba(0, 0, 0, .04); padding: 5px;">
      <el-col :span="8">
        <div class="mystep">
          <p>选择滑动窗口步长</p>
          <el-select v-model="value" placeholder="请选择滑窗步长">
            <el-option
              v-for="item in options"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </div>
      </el-col>
      <el-col :span="8">
        <div>
          <p>选择变化区域的颜色</p>
          <div class="mycolor">
            <el-color-picker
              v-model="color"
              show-alpha
              :predefine="predefineColors"
            />
          </div>
        </div>
      </el-col>
      <el-col :span="8">
        <div class="myconfidence" style="margin-top:30px">
          <span class="myfont">置信度阈值</span>
          <el-slider v-model="confidence" :format-tooltip="formatTooltip" :min="0.1" :max="0.9" :step="0.1" show-input />
        </div>
      </el-col>
    </el-row>
    <el-row style="margin:20px">
      <el-col :span="12">
        <div class="tip">
          点击上传前时相遥感图
        </div>
        <el-upload
          class="avatar-uploader"
          action="#"
          :headers="headers"
          list-type="picture-card"
          accept=".jpg, .jpeg, .png"
          :name="name1"
          :limit="2"
          :file-list="fileList1"
          :show-file-list="false"
          :auto-upload="false"
          :on-change="change1"
          :before-upload="handleBefore"
          style="text-align: center; padding-top:10px;padding-bottom:10px;height:auto;"
        >
          <img v-if="dialogImageUrl1" :src="dialogImageUrl1" class="avatar">
          <i v-else class="el-icon-upload" />
        </el-upload>
      </el-col>
      <el-col :span="12">
        <div class="tip">
          点击上传后时相遥感图
        </div>
        <el-upload
          class="avatar-uploader"
          action="#"
          :headers="headers"
          list-type="picture-card"
          accept=".jpg, .jpeg, .png"
          :name="name2"
          :limit="2"
          :file-list="fileList2"
          :show-file-list="false"
          :auto-upload="false"
          :on-change="change2"
          :before-upload="handleBefore"
          style="text-align: center; padding-top:10px;padding-bottom:10px;height:auto;"
        >
          <img v-if="dialogImageUrl2" :src="dialogImageUrl2" class="avatar">
          <i v-else class="el-icon-upload" />
        </el-upload>
      </el-col>
    </el-row>
    <el-row style="text-align: center; padding-top:10px;padding-bottom:30px; margin:20px;">
      <el-button type="primary" round :loading="loading" @click="doChangeDetection()">变化检测</el-button>
    </el-row>
    <el-row>
      <div v-show="resvisible" class="tip">
        变化检测结果如下
      </div>
      <div class="tip">
        <el-image
          v-show="resvisible"
          :src="resultsrc"
          :preview-src-list="[resultsrc]"
          style="text-align: center; width: 40%; height: 40%;"
        />
        <el-image
          v-show="resvisible"
          :src="gifsrc"
          :preview-src-list="[gifsrc]"
          style="text-align: center; width: 40%; height: 40%;"
        />
      </div>
      <el-row v-show="resvisible" style="text-align: center; padding-top:10px;padding-bottom:30px;">
        <el-button type="primary" round @click="saveResult()">保存结果</el-button>
      </el-row>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'
// import * as mammoth from 'mammoth'
import { saveAs } from 'file-saver'
export default {
  data() {
    return {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      fileList1: [],
      fileList2: [],
      resultsrc: '',
      gifsrc: '',
      name1: 'sensingbefor',
      name2: 'sensingafter',
      dialogImageUrl1: '',
      dialogImageUrl2: '',
      options: [{
        value: '64',
        label: 'Step: X64'
      }, {
        value: '128',
        label: 'Step: X128'
      }, {
        value: '192',
        label: 'Step: X192'
      }, {
        value: '256',
        label: 'Step: X256'
      }],
      value: '64',
      confidence: 0.5,
      color: 'rgba(255, 0, 0, 0.67)',
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
      dialogVisible1: false,
      dialogVisible2: false,
      resvisible: false,
      loading: false
    }
  },
  methods: {
    // 保存纠错结果
    saveResult() {
      var tempData = ''
      tempData = this.dataURLtoBlob(this.resultsrc)
      if (tempData === '') {
        this.$message({
          showClose: true,
          message: '内容为空,保存失败！',
          type: 'warning'
        })
      } else {
        var tempResult = new Blob([tempData], { type: 'image/jpg' })
        saveAs(tempResult, 'changeres.jpg')
      }
    },
    doChangeDetection() {
      var that = this
      that.loading = true
      const formData = new FormData()
      if (that.fileList1.length === 0 || that.fileList2.length === 0) {
        this.$message({
          showClose: true,
          message: '请先选择要进行变化检测的图片！',
          type: 'warning'
        })
        that.resultsrc = ''
        that.resvisible = false
        that.loading = false
        return
      } else {
        formData.append(that.name1, that.fileList1[0].raw)
        formData.append(that.name2, that.fileList2[0].raw)
        formData.append('STEP', that.value)
        formData.append('COLOR', that.color)
        formData.append('CONFIDENCE', that.confidence)
        // 请求后端API服务，请求方法为post，请求体字段为json格式 text
        axios.post('http://10.1.114.93:5000/v1/changedetection',
          formData
        ).then((response) => {
          if (response.status === 'ok') {
            console.log('上传成功')
          }
          // const src = window.URL.createObjectURL(response.data)
          const src = 'data:image/jpeg;base64,' + response.data.changeres
          const gifsrc = 'data:image/gif;base64,' + response.data.gif
          that.resultsrc = src
          that.gifsrc = gifsrc
          that.resvisible = true
          that.loading = false
          that.$message({
            showClose: true,
            message: '变化检测完成！',
            type: 'success'
          })
        }).catch((error) => {
          console.log(error)
          that.resultsrc = ''
          that.gifsrc = ''
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
    change1(file, fileList1) {
    // 将每次图片数组变化的时候，实时的进行监听，更改数组里面的图片数据
      if (fileList1.length > 0) {
        this.fileList1 = [fileList1[fileList1.length - 1]]
        this.dialogImageUrl1 = URL.createObjectURL(file.raw)
      }
    },
    change2(file, fileList2) {
    // 将每次图片数组变化的时候，实时的进行监听，更改数组里面的图片数据
      if (fileList2.length > 0) {
        this.fileList2 = [fileList2[fileList2.length - 1]]
        this.dialogImageUrl2 = URL.createObjectURL(file.raw)
      }
    },
    handleBefore(file) {
      // 判断图片是否大于2M
      const isLt2M = file.size / 1024 / 1024 < 2
      // const fileType = file.name.substring(file.name.lastIndexOf('.')+1)
      // 判断图片的类型
      const isJpg = file.type === 'image/jpeg' || file.type === 'image/jpg' || file.type === 'image/png'
      if (!isJpg) {
        this.$message.error('只能上传jpg, jpeg, png, gif格式的图片！')
        return false
      }
      if (!isLt2M) {
        this.$message.error('上传图片大小不能超过 2MB!')
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
  .el-icon-upload {
    font-size: 28px;
    color: #8c939d;
    width: 300px;
    height: 300px;
    line-height: 300px;
    text-align: center;
  }
  .avatar {
    width: 300px;
    height: 300px;
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
    width: 300px;
    height: 300px;
    line-height: 146px;
    vertical-align: top;
}
</style>

