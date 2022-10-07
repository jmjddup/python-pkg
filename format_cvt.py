'''
Date: 2022-10-05 01:04:44
LastEditors: error: git config user.name && git config user.email & please set dead value or install git
LastEditTime: 2022-10-07 10:15:24
FilePath: /jmj/workspace/python-pkg/format_cvt.py
Description: 
'''
import os
import numpy as np
import random


'''
description: convert float data to its binary representation
param: float data
return: uint represetation of binary data
'''
def float2bin(fdata):
    return np.frombuffer(np.float32(fdata).tobytes(), dtype=np.uint32)[0]

'''
description: convert binary data to its float representation
param: uint representation of binary data
return: float data
'''
def bin2float(bdata):
    return np.frombuffer(np.uint32(bdata).tobytes(), dtype=np.float32)[0]

def FloatToInt32(fdata):
    return np.frombuffer(np.float32(fdata).tobytes(), dtype=np.int32)[0]
def Int32ToFloat(data):
    return np.frombuffer(np.int32(data).tobytes(), dtype=np.float32)[0]

constImplied1 = 0x00800000
constMantMask = 0x007fffff
constMaxInt = 0x7fffffff
constMaxExp = 0x20000000
constNegMaxExp = 0xe0000000
'''
description: convert float data to its qf32(Exp/Mant) representation 
param: { fdata: float data }
return: { qf32 data: (Exp, Mant) data }
'''
def float_to_qf32(fdata):
    # step 1: convert float data to its binary representation
    bdata_uint = float2bin(fdata)
    bdata_int = np.frombuffer(np.float32(fdata).tobytes(), dtype=np.int32)[0]
    
    # step 2: convert binary to its Exp/Mant representation
    tmpExp = bdata_uint >> 23 & 0xff
    tmpMant = bdata_uint & constMantMask | constImplied1

    pred0 = 1 if (0 > bdata_int) else 0
    pred1 = 1 if (tmpExp == 255) else 0
    pred2 = 1 if (tmpExp == 0) else 0

    tmpExp = tmpExp - 126
    tmpExp = constMaxExp if pred1 else tmpExp
    tmpExp = constNegMaxExp if pred2 else tmpExp
    tmpMant = tmpMant << 7
    tmpMant = constMaxInt if pred1 else tmpMant
    tmpMant = -tmpMant if pred0 else tmpMant
    tmpMant = 0 if pred2 else tmpMant

    return (tmpExp, tmpMant)

def qf32_to_float(qfdata, even_rounding=False):
    # step 1: convert qfdata(Exp/Mant) to its binary representation
    exp, mant = qfdata

    constRound = 64
    pred3 = 1 if (0 > mant) else 0
    if even_rounding:
        odd = mant & 0x80
        constRound = (constRound - 1) if (~odd) else constRound
    mant = mant + constRound

    exp = exp + 126
    pred0 = 1 if (255 > exp) else 0
    pred0 &= 1 if (exp > 0) else 0
    exp = min(exp, 255)
    exp = max(exp, 0)

    mant = mant >> 7
    pred1 = 1 if(mant == 0xff000000) else 0
    mant = abs(mant)
    mant = mant & constMantMask
    exp = (exp + 1) if pred1 else exp
    sign = 0x80000000 if pred3 else 0x00000000
    exp = exp << 23
    exp = sign | exp
    exp = (exp + mant) if pred0 else exp
    # step 2: convert binary to its float representation
    return bin2float(exp)

'''
description: convert data from format A to B 
param: { data: the data which has format A; formA: origin format A of the data; formB: the format B needs to convert }
return: the data of format B
'''
def formA2formB(data, formA, formB):
    methods_ = {
        ('fp32'     , 'bin'     ) : float2bin,
        ('bin'      , 'fp32'    ) : bin2float,
        ('fp32'     , 'uint32'  ) : float2bin,
        ('uint32'   , 'fp32'    ) : bin2float,

        ('fp32'     , 'int32'   ) : FloatToInt32,
        ('int32'    , 'fp32'    ) : Int32ToFloat,

        ('fp32'     , 'qf32'    ) : float_to_qf32,
        ('qf32'     , 'float'   ) : qf32_to_float
    }
    method = methods_.get((formA, formB)) # type(method): class 'function'
    if method:
        odata = method(data)
    return odata

def test():
    data = 2.5
    # print(formA2formB(data, 'fp32', 'bin'))
    # print(qf32_to_float(float_to_qf32(data)))
    print(formA2formB(data, 'fp32', 'qf32'))

def main():
    test()

if __name__ == '__main__':
    main()