# 重力体感灯



## 概述

有这个想法，是来源于哔哩哔哩上的一个[视频](https://www.bilibili.com/video/BV1iJ411H7JS?from=search&seid=9296495138958509718&spm_id_from=333.337.0.0)，它转载于[油管上的一个视频](https://www.youtube.com/watch?v=dueJTClX7c4)。所以，我复现了一下。

## 硬件

> 1、ws2812像素屏一块（16*16）
>
> 2、树莓派4B
>
> 3、Mpu6060
>
> 4、稳压电源5V3A
>
> 5、导线若干

## 软件

> 1、Raspberry Pi OS
>
> 2、mpu6050 库
>
> 3、ws2812 库
>
> 4、该项目的算法

## 实现过程

> 1、首先，接好所有的硬件设备，按照下图
> ![image-20211212122356857](https://gitee.com/lmz2498369702/image-repository/raw/master/202112121223983.png)

> 2、编写程序
>
> 程序可以直接运行
>
> 3、运行命令
>
> ```python
> sudo python3 main.py
> ```

