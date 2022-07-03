import request from '@/utils/request'

export function ChangeDetec(params) {
  return request({
    url: 'http://10.1.114.93:5000/v1/changedetection',
    method: 'post',
    params
  })
}

export function ObjectDetec(params) {
  return request({
    url: 'http://10.1.114.93:5000/v1/objectdetection',
    method: 'post',
    params
  })
}

export function DiwiClas(params) {
  return request({
    url: 'http://10.1.114.93:5000/v1/diwuclassification',
    method: 'post',
    params
  })
}

export function ObjectExtrac(params) {
  return request({
    url: 'http://10.1.114.93:5000/v1/objectextraction',
    method: 'post',
    params
  })
}

// export function ChangeDetec(params) {
//   return request({
//     url: 'http://10.1.114.93:5000/v1/changedetection',
//     method: 'post',
//     params
//   })
// }

export function BatchObjectDetec(params) {
  return request({
    url: 'http://10.1.114.93:5000/v1/batchobjectdetection',
    method: 'post',
    params
  })
}

export function BatchDiwiClas(params) {
  return request({
    url: 'http://10.1.114.93:5000/v1/batchdiwuclassification',
    method: 'post',
    params
  })
}

export function BatchObjectExtrac(params) {
  return request({
    url: 'http://10.1.114.93:5000/v1/batchobjectextraction',
    method: 'post',
    params
  })
}

