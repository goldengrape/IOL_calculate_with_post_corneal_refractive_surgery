#!/usr/bin/env python
# coding: utf-8

# # 角膜屈光手术后的人工晶体计算
# 
# 本文是参考这篇文献：[Intraocular lens power calculation in eyes with previous corneal refractive surgery](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6053834/)
# 
# 目的：
# * 动手算一遍各种角膜屈光术后的人工晶体计算
#     * 要理解整个问题，自己动手推导一遍才是最好的。
#     * 而且，由于有那么多的公式，所以能够自己同时算出几个公式的结果，综合考虑，才是临床上比较保险的方法。
# * 顺便练习交互式的Ipython
#     * 要在jupyter上运行交互式的控件，比如滑动条之类，又懒得做一个GUI的图形界面。就需要使用ipywidgets这个库。关于ipywidgets的详细说明，请参考[ipywidgets的文档](https://ipywidgets.readthedocs.io/)也可以参考这个[15页python教程中的简单介绍](https://github.com/goldengrape/PartIA-Computing-Michaelmas-zh-CN/blob/master/zh-CN/08%20Plotting.ipynb)，我在这里仅仅使用的是基本功能。

# In[34]:


# try:
#     import ipywidgets as widgets
#     from ipywidgets import interact, interact_manual, fixed
# except:
#     !conda install -c conda-forge ipywidgets
#     import ipywidgets as widgets
#     from ipywidgets import interact, interact_manual, fixed

import ipywidgets as widgets
from ipywidgets import interact, interact_manual, fixed


# ## 角膜屈光手术后，IOL为什么会算错？
# 

# ### keratometric index error
# 
# keratometric index ，大概可以翻译成“角膜测量折射率”，看起来这像是个历史遗留问题：
# 
# 1. 要测量角膜曲率，可以用角膜曲率计（包括自动验光仪和IOL Master）或者角膜地形图，
#     * 角膜曲率计是通过测量角膜**前表面**的反光，参考[角膜曲率计的起源及其在眼科学中的演变作用](sci-hub.tw/10.1016/j.survophthal.2010.03.001)
#     * 以Placido环为原理的角膜地形图，是测量角膜**前表面**的反射像。
# 
#     这两种方式都导致只能测量角膜前表面的形态。
# 1. 测量角膜曲率虽然度数是K，单位是D，可以直接带入到屈光度的计算中去。但实际只是测量了角膜的形态，得到的是“曲率半径”

# 因此，从角膜曲率计、角膜地形图、甚至IOL Master上读取到的角膜曲率这个数值是一个从测量值经过推导以后的结果。既然是推导之后的，就“有人”在里面做了手脚。
# 
# 角膜有前后表面，光线在经过前后表面的时候都发生了折射。前后表面对角膜的屈光力来说都起了作用。但是在常见的IOL计算公式中，关于角膜屈光度的数据，只使用了一个K，比如最简单的SRK公式中
# $$
# IOL=A - 0.9 \times K -2.5 \times AL 
# $$
# 
# 这个单一的K，是角膜前后表面屈光力叠加的结果。为了能够与叠加的结果等效，所以将角膜简化为单一的曲面，其折射率**人为设定**成1.3375，而实际上，如果真正切下来一块角膜基质进行测量，其折射率为1.376。

# #### 薄透镜的屈光度
# $$
# P=\frac{n_2-n_1}{r}
# $$
# 其中，$n_1, n_2$是界面两侧的折射率，r是曲率半径，单位是米。得到的是屈光度。
# 如果考虑角膜前表面，那么$n_1=1$是空气。

# In[36]:


def thin_lens_power(n1=1,n2=1.3375,r=7.5):
    return (n2-n1)/(r/1000) #如果使用毫米，则需要除以1000，以转换为米


# 通过interact，可以为函数建立一个滑动条。现在请试着改变r值，看看屈光度的变化过程。

# In[43]:


interact(thin_lens_power, 
         n1=fixed(1), 
         n2=1.3375, 
         r=widgets.FloatSlider(min=6, max=8, step=0.01, value=7.5));


# 当角膜前表面的曲率半径=7.5毫米时，角膜前后表面屈光度之和为45D时，“需要的”折射率恰好是1.3375

# 这种合并角膜前后表面，用一个折射率来替代的方案，内部隐含了一个假设：
# > 假设角膜前后表面的曲率半径是成比例的。
# 
# 而这个假设，显然在做完角膜屈光手术以后，被打破了！
# 
# 那么，在角膜屈光手术以后，通过角膜曲率计测量的原始数值，还在使用1.3375来换算出一个K值，这个K并不是当前角膜前后表面曲率的联合了。将这个K值代入到人工晶体的计算公式中将引出一系列错误。

# In[ ]:




