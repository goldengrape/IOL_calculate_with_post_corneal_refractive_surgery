[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/goldengrape/IOL_calculate_with_post_corneal_refractive_surgery/master)

# 角膜屈光手术后的人工晶体计算

本文是参考这篇文献：[Intraocular lens power calculation in eyes with previous corneal refractive surgery](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6053834/)

## 目的：

* 动手算一遍各种角膜屈光术后的人工晶体计算
    * 要理解整个问题，自己动手推导一遍才是最好的。
    * 而且，由于有那么多的公式，所以能够自己同时算出几个公式的结果，综合考虑，才是临床上比较保险的方法。
* 顺便练习交互式的Ipython
    * 要在jupyter上运行交互式的控件，比如滑动条之类，又懒得做一个GUI的图形界面。就需要使用ipywidgets这个库。关于ipywidgets的详细说明，请参考[ipywidgets的文档](https://ipywidgets.readthedocs.io/)也可以参考这个[15页python教程中的简单介绍](https://github.com/goldengrape/PartIA-Computing-Michaelmas-zh-CN/blob/master/zh-CN/08%20Plotting.ipynb)，我在这里仅仅使用的是基本功能。

## 使用

将包含两个部分，一个是依照参考文献顺序推导，一个是综合的角膜屈光手术后IOL度数计算器，把文中提到的各种计算公式都实现出来，输入数据以后列出各种公式所得到的计算结果，供临床医生参考。