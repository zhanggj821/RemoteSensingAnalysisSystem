import re
import numpy as np

# color = 'rgba(255, 69, 0, 0.68)'

# def parsecolor(color):
#     partten = r'\d+\.\d+|\d+'
#     res = re.findall(partten, color)
#     lut = [0,0,0,0]
#     lut[0] = int(res[0])
#     lut[1] = int(res[1])
#     lut[2] = int(res[2])
#     lut[3] = int(float(res[3])*255)
#     # res = np.array(res)
#     return lut

# res = parsecolor(color)
# print(res)

# a = [1,2,3,4]
# b = [i*0 for i in a]
# print(b)

filename = 'qqqq.tiff'
if(filename.endswith('png') is False):
    filename = list(filename)
    index = filename.index('.')
    filename[index+1:] = 'png'
    filename = ''.join(filename)
    print(filename)