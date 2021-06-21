#pragma once
#include "camCompilerConfig.h" 
extern "C" {
//ctypes默认函数的返回值应该是 C int类型的. 其他类型的返回值则要使用函数对象的 restpye 属性来设置
// ctypes 返回类型bool时，得到非0数， 暂时搞不清楚什么原因，咱改为返回int
/*
 * >>> strchr = libc.strchr
>>> strchr(b"abcdef", ord("d"))
8059983            # 这里ctypes并不知道返回的是什么,所以默认直接就把指针地址打印了出来(int型)
>>> strchr.restype = c_char_p   # c_char_p is a pointer to a string
>>> strchr(b"abcdef", ord("d"))
b'def'             # 这里设置过了,ctypes知道返回的是c_char_p类型,所以打印该指针指向的字符串数据
*/
void CAMERA_API init();
void CAMERA_API finit();

// 重载
int CAMERA_API connectCam();
int CAMERA_API disConnect();
int CAMERA_API open();
int CAMERA_API close();
int CAMERA_API run();
int CAMERA_API stop();

// 设置参数相关
// 设置曝光时间等级0，1，2，3，4
int CAMERA_API setExposureGrad(int grad=2);
int CAMERA_API setExposure(int ms);

// 采集图像
int CAMERA_API capture(unsigned char* buf, int buflen, int nchs);
int CAMERA_API captureOneImg(unsigned char* buf, int buflen, int nchs);

// 设置图像尺寸
int CAMERA_API setImgSize(int width, int height);
int CAMERA_API getImgWidth();
int CAMERA_API getImgHeight();

// 设置X镜像
int CAMERA_API setReverseX(bool isReverse = true);

// 设置centerXY
int CAMERA_API setCenterX(bool isCen = true);
int CAMERA_API setCenterY(bool isCen = true);

// 获取错误信息
int CAMERA_API getError(char* msg, int buflen);

// 状态
int CAMERA_API isConnected();
int CAMERA_API isOpened();
int CAMERA_API isContinueCaptured();
int CAMERA_API isRun();
int CAMERA_API isIdle();

}
