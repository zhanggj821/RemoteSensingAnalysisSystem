<template>
  <div class="app-container" style="overflow: auto;">
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
    <el-row style="margin:20px">
      <div class="tip">
        请上传要检测的遥感图
      </div>
      <el-upload
        class="avatar-uploader"
        action="#"
        :headers="headers"
        list-type="picture-card"
        accept=".jpg, .jpeg, .png"
        :name="name"
        :limit="2"
        :file-list="fileList"
        :show-file-list="false"
        :auto-upload="false"
        :on-change="change"
        :before-upload="handleBefore"
        style="text-align: center; padding-top:10px;padding-bottom:10px;height:auto;"
      >
        <img v-if="dialogImageUrl1" :src="dialogImageUrl1" class="avatar">
        <i v-else class="el-icon-upload" />
      </el-upload>
    </el-row>
    <el-row style="text-align: center; padding-top:10px;padding-bottom:30px;">
      <el-button type="primary" round :loading="loading" @click="doClassification()">地物分类</el-button>
    </el-row>
    <el-row style="text-align: center;" />
    <div v-show="resvisible" class="tip" style="margin-top:10px;">
      检测结果如下
    </div>
    <div class="tip">
      <el-image
        v-show="resvisible"
        :src="resultsrc"
        :preview-src-list="[resultsrc]"
        style="text-align: center; width: 40%; height: 40%;"
      />
    </div>
    <el-row v-show="resvisible" style="text-align: center; padding-top:10px;padding-bottom:30px;">
      <el-button type="primary" round @click="saveResult()">保存结果</el-button>
    </el-row>
  </div>
</template>

<script>
import axios from 'axios'
// import * as mammoth from 'mammoth'
import { saveAs } from 'file-saver'
const LabelOptions = ['建筑', '耕地', '林地', '水体']
export default {
  data() {
    return {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      fileList: [],
      resultsrc: '',
      name: 'senseimage',
      dialogImageUrl1: '',
      dialogVisible: false,
      resvisible: false,
      disabled: false,
      loading: false,
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
        saveAs(tempResult, 'classres.jpg')
      }
    },
    doClassification() {
      var that = this
      that.loading = true
      const formData = new FormData()
      if (that.dialogImageUrl1 === '') {
        this.$message({
          showClose: true,
          message: '请先选择要进行检测的图片！',
          type: 'warning'
        })
        that.resultsrc = ''
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
        console.log(selectlabels)
        // 请求后端API服务，请求方法为post，请求体字段为json格式 text
        axios.post('http://10.1.114.93:5000/v1/diwuclassification',
          formData
        ).then((response) => {
          if (response.status === 'ok') {
            console.log('上传成功')
          }
          // const src = window.URL.createObjectURL(response.data.result)
          const src = 'data:image/jpeg;base64,' + response.data.clares
          that.resultsrc = src
          that.resvisible = true
          that.loading = false
          that.$message({
            showClose: true,
            message: '地物分类完成！',
            type: 'success'
          })
        }).catch((error) => {
          console.log(error)
          that.resultsrc = ''
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
    // 全选
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
  .myfont {
    font-family: 宋体;
  font-size: 18x;
	font-weight:normal;
  width: 100%;
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
  /* .avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 300px;
    height: 300px;
    line-height: 300px;
    text-align: center;
  } */
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

