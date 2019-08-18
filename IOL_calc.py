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

# In[1]:


# try:
#     import ipywidgets as widgets
#     from ipywidgets import interact, interact_manual, fixed
# except:
#     !conda install -c conda-forge ipywidgets
#     import ipywidgets as widgets
#     from ipywidgets import interact, interact_manual, fixed

import ipywidgets as widgets
from ipywidgets import interact, interact_manual, fixed
from compute_IOL import Double_K_SRK_T, SRK_T, HOFFER_Q, shammas, Haigis_L, BESST


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
# \tag 1
# $$
# 其中，$n_1, n_2$是界面两侧的折射率，r是曲率半径，单位是米。得到的是屈光度。
# 如果考虑角膜前表面，那么$n_1=1$是空气。

# In[2]:


def thin_lens_power(n1=1,n2=1.3375,r=7.5):
    return (n2-n1)/(r/1000) #如果使用毫米，则需要除以1000，以转换为米


# 通过interact，可以为函数建立一个滑动条。现在请试着改变r值，看看屈光度的变化过程。

# In[3]:


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

# ### 角膜曲率半径测量错误
# 
# 很多设备, 尤其是Placido环为基础的角膜地形图, 角膜正中央的曲率半径是测不了的, 只能从周边的数据进行外推. 角膜屈光手术以后, 中央切平了一些, 而周边还是比较陡峭的, 那么如果按照周边进行外推, 很可能推错. 尤其是对于切削区域比较小的, 或者是切削偏中心的病例, 可能影响更大.

# ### 公式错误
# 
# 计算IOL度数的公式, 发展到第三代, Hoffer Q, Holladay 1 and SRK/T, 使用角膜曲率作为参数来预测“有效晶体位置”ELP. 但如果近视激光手术, 角膜切平了, 这些公式就可能会低估ELP的位置. 而远视的屈光手术, 角膜更陡峭一些, 这些公式则会高估ELP位置.
# 
# 这个问题只对使用角膜曲率来估计ELP的公式才存在, Haigis不受影响.

# # 病史数据已知

# 当患者具备以下资料时：
# 
# * 术前的角膜曲率测量数据
# * 或，屈光度变化量
# 
# 可以使用下面这些公式的推导

# ## 修正角膜曲率K

# ### 已知角膜屈光手术之前的K值
# Seitz/Speicher’s 方法
# 
# 已知当前通过角膜曲率计测量出来的K值是个诡异的错误。那么要得到真正的K值，需要这些推导：

# $$
# P=P_a+P_p = \frac{n_2-n_1}{r_1}+\frac{n_3-n_2}{r_2}
# \tag 2
# $$
# 
# 其中：$P_a$是角膜前表面屈光度, $P_p$是角膜后表面屈光度, $n_1=1$(空气), $n_2=1.376$(角膜), $n_3=1.336$(房水)

# 现在从角膜曲率计上读取的K度数, 只是机器得到了角膜曲率半径以后, 从1.3375计算出来的K值, 避免混淆使用SimK来代表.
# 
# 那么真实的角膜前表面屈光度是多少呢?
# 由(1)式
# $$
# P=\frac{n_2-n_1}{r}
# \tag 1
# $$
# 可以得知r的计算, 注意此处只是逆向计算角膜曲率计的过程,所以$n_2$用虚拟折射率1.3375
# $$
# r=\frac{n_2(1.3375)-n_1}{P}
# =\frac{1.3375-1}{SimK}
# =\frac{0.3375}{SimK}
# $$
# 在将r代入到$P_a$的计算过程, 注意这里是计算真实的角膜前表面屈光力, 折射率应该代入1.376
# $$
# P_a=\frac{n_2(1.376)-n_1}{r}
# =\frac{1.376-1}{\frac{0.3375}{SimK}}
# =SimK\times \frac{0.376}{0.3375}
# =SimK \times 1.114
# \tag 3
# $$
# 

# In[4]:


def true_power_of_anterior_corneal(SimK):
    return SimK*0.376/0.3375


# In[5]:


interact(true_power_of_anterior_corneal, 
         SimK=widgets.FloatSlider(min=35, max=55, step=0.5, value=44));


# 那么角膜后表面的屈光力$P_p$, 就可以算出来了
# $$
# \mathrm{P}_{\mathrm{p}}=\mathrm{P}-\mathrm{P}_{\mathrm{a}}=\operatorname{SimK} - (\operatorname{Sim} \mathrm{K} \times 1.114)
# \tag 4
# $$
# 
# 注意, 这里我写的公式与参考论文中的相反, 严格按照数学运算来, 没有擅自取绝对值改变符号. 否则后续的过程容易出纰漏

# In[6]:


def true_power_of_posterior_corneal(SimK):
    return SimK-true_power_of_anterior_corneal(SimK)


# In[7]:


interact(true_power_of_posterior_corneal, 
         SimK=widgets.FloatSlider(min=35, max=55, step=0.5, value=44));


# 接下来要绕一些. 先分清楚角膜屈光手术之前会测一个K值, SimK, 我们叫做preopSimK, Lasik术前的时候, 角膜前表面没有被切平过, 所以前后表面的半径还满足预设的比例关系, 是可以用preopSimK来推算后表面屈光力Pp的; 而做完了Lasik手术以后, 再测量SimK, 我们叫做postopSimK, 这个时候角膜前表面已经被切薄了, 前后表面的半径比例关系被打破了, postopSimK只能用来计算前表面的屈光力Pa,不能用来计算后表面的屈光力Pp.
# 
# 于是就有了下面这个公式:

# $$
# \mathrm{P}=\text { postpop } \mathrm{P}_{\mathrm{a}}+\mathrm{P}_{\mathrm{p}}=\text { postpop } \operatorname{Sim} \mathrm{K} \times 1.114+(\text { preop }- \text { preop } \operatorname{SimK} \times 1.114)
# \tag 5
# $$
# 
# 注意: 这里严格按数学过程推导公式, 与参考论文中的$P_p$符号相反

# In[8]:


def true_K(preopSimK, postopSimK):
    P = true_power_of_anterior_corneal(postopSimK) +         true_power_of_posterior_corneal(preopSimK)
    return P


# In[9]:


interact(true_K,
        preopSimK=widgets.FloatText(value = 44),
        postopSimK=widgets.FloatText(value= 42));


# 如果有以前的手术记录, 那么填入角膜屈光手术之前检查的角膜K值, 作为preopSimK, 最近再查一次角膜K值, 作为postopSimK, 计算以后得出角膜真实的K值, 这时可以考虑使用Double-K SRK/T公式计算IOL度数了.

# In[10]:


def Double_K_SRK_T_with_true_K(AL, preopSimK, postopSimK, A, REFt):
    Kpre=preopSimK
    Kpost=true_K(preopSimK, postopSimK)
    return Double_K_SRK_T(AL, Kpre, Kpost, A,REFt)


# In[11]:


interact(Double_K_SRK_T_with_true_K,
        AL=widgets.FloatText(value=23.5),
        preopSimK=widgets.FloatText(value=44),
        postopSimK=widgets.FloatText(value=43),
        A=widgets.FloatText(value=118.4),
        REFt=widgets.FloatText(value=-0.5));


# ### 已知角膜屈光手术引入的屈光度差值
# 
# 如果找不到角膜屈光手术之前测量的角膜K值, 比如没有复印热敏打印的结果, 又没有在病历里记录. (应该不至于吧). 但是可以从手术记录里找到手术做了多少屈光度. 也就是 SIRC, surgical induced refractive change. 那么也可以算. 
# 
# 此时假设角膜后表面的屈光力是平均值-4.98D. 那么也可以不修改K值, 而是去修正keratometric index, 将1.3375这个数据修改掉.
# 
# * [Savini的方法](https://www.ncbi.nlm.nih.gov/pubmed/17523506/): $ n_{post} = 1.338 + 0.0009856\times SIRC $ (适用于近视)
# * [Camellin的方法](https://www.ncbi.nlm.nih.gov/pubmed/16523839/): $ n_{post} = 1.3319 + 0.00113 \times SIRC $
# * [Jarade的方法](https://www.ncbi.nlm.nih.gov/pubmed/16447940/): $ n_{post} = 1.3375 + 0.0014 \times SIRC $
# 
# 这三种方法的文献都是发在Journal of Refractive Surgery上, 但Journal of Refractive Surgery上说“2012年1月之前的文章是后台文件集的一部分，不适用于当前付费订阅。 要访问该文章，您可以在此处购买或购买完整的后台文件集”, 似乎是把老文章都压缩起来了. 于是这三篇文章的全文在sci-hub上我也没有找到. 
# 

# In[12]:


def n_post(SIRC, method="savini"):
    parameters={"savini":[1.338, 0.0009856],
                "camellin":[1.3319, 0.00113],
                "jarade": [1.3375,  0.0014],
               }
    m=method.lower()
    n = parameters[m][0]+parameters[m][1]* SIRC
    return n


# In[13]:


interact(n_post,
         SIRC=widgets.FloatSlider(min=-10, max=+5, step=0.25, value=-3),
         method=["savini", "camellin", "jarade"]
        );


# 得到修正过的折射率以后, 根据(1)式, 计算新的K值
# $$
# P=\frac{n_2-n_1}{r}
# \tag 1
# $$

# In[14]:


def true_K_based_on_SIRC(SimK, SIRC, method="savini"):
    n_2=n_post(SIRC, method)
    r=(1.3375-1)/SimK
    p=(n_2-1)/r
    return p


# In[15]:


interact(true_K_based_on_SIRC,
         SimK=widgets.FloatText(value=43),
         SIRC=widgets.FloatText(value=-3),
         method=["savini", "camellin", "jarade"]
        );


# 得到的K值, 应该代入到 Double-K SRK/T公式中, 计算IOL度数.
# 
# 此处有一些模糊, 计算出来的是 n(post) = 1.338 + 0.0009856 x, 也就是说是角膜屈光手术之后的n, 根据这个n, 算出来的就应该是Kpost, 那么角膜屈光手术之前的Kpre呢? 也仍然是要有这个记录的么?

# In[16]:


def Double_K_SRK_T_with_true_K_based_on_SIRC(AL,preopSimK, SimK,  A, REFt, SIRC, method="savini"):
    Kpre=preopSimK    
    Kpost=true_K_based_on_SIRC(SimK, SIRC, method)
    return Double_K_SRK_T(AL, Kpre, Kpost, A,REFt)


# In[17]:


interact(Double_K_SRK_T_with_true_K_based_on_SIRC,
        AL=widgets.FloatText(value=23.5),
        preopSimK=widgets.FloatText(value=44),
        SimK=widgets.FloatText(value=43),
        A=widgets.FloatText(value=118.4),
        REFt=widgets.FloatText(value=-0.5),
        SIRC=widgets.FloatText(value=-3),
        method=["savini", "camellin", "jarade"]
        );


# ### 直接修正IOL计算结果
# 
# 还有一组研究者, 直接把角膜屈光手术修正的度数SIRC, 和IOL计算结果直接联系起来, 计算出一个修正量. 直接加到IOL计算结果里面就是了. 这里的IOL结果, 可以由Single-K SRK/T (近视) 或者 Single-K Hoffer Q (远视) 来计算. 
# 
# * Masket的方法: $\Delta IOL = SIRC \times (−0.326) + 0.101 $
# * [Latkany的方法](https://sci-hub.tw/10.1016/j.jcrs.2004.06.053) : 用屈光手术前的等效球镜度数RXpre(原始文献中称为SEQm)来计算. 代入SRK/T公式的时候, 根据使用的K值不同, 有两种
#     * 使用K1,K2的平均值代入代入SRK/T公式时: $\Delta IOL= −(0.46 \times RXpre + 0.21) $ 
#     * 使用最平坦的K 代入SRK/T公式时 :  $\Delta IOL= -(0.47 \times RXpre + 0.85) $ 
#     * 当计算屈光术前是远视的患者时:$\Delta IOL= −(0.27 \times RXpre + 1.53) $

# In[18]:


def delta_IOL_power_masket(SIRC):
    return SIRC*(-0.326+0.101)
def delta_IOL_power_latkany(RXpre, Ktype="avg"):
    if RXpre >0:
        delta_IOL= -1*(0.27 * RXpre + 1.53)
    elif Ktype.lower()=="avg":
        delta_IOL= -1*(0.46 * RXpre + 0.21)
    elif Ktype.lower()=="flattest":
        delta_IOL= -1*(0.47 * RXpre + 0.85)
    return delta_IOL


# In[19]:


interact(delta_IOL_power_masket, SIRC=-3);
interact(delta_IOL_power_latkany, RXpre=-3, Ktype=["avg","flattest"]);


# [Awwad’s 的方法](https://sci-hub.tw/10.1016/j.jcrs.2008.03.020):一口气搞出了6个公式, 就看现在手里有哪些数据了. (简直是练习函数重载的例题), 其中几个参数先解释下:
# * $ACCP_{3mm}$ 这是使用Placido环原理的角膜地形图测量出来的中央角膜3mm直径内的平均屈光力. 与角膜曲率计测量出来的SimK不同, Placido环的原理决定了正中央的角膜曲率是测不出来的, 只能从周围的数据外推得到. 学究气我喜欢.
# * $SE_{preLASIK}, SE_{postLASIK}$, Lasik手术前后的等效球镜. 两者之差$SE_{postLASIK} - SE_{preLASIK})$显然就是手术做掉的屈光度SIRC
# * $K_{preLASIK}$, Lasik术前的角膜曲率K, 相当于前面公式里的preopSimK

# * Parameter set 1: $ ACCP_{3mm}, \space and \space  (SE_{postLASIK},  SE_{preLASIK}) $
#   * $ ACCP_{adj}=ACCP_{3mm} - 0.16\times(SE_{postLASIK} - SE_{preLASIK}) $
#   
# * Parameter set 2: $ SimK, \space and \space (SE_{postLASIK},  SE_{preLASIK})$
#   * $ SimK_{adj}= SimK - 0.23 \times (SE_{postLASIK} - SE_{preLASIK})$
#   
# * Parameter set 3: $ ACCP_{3mm}, \space(SE_{postLASIK} , \space SE_{preLASIK})), and \space K_{preLASIK} $
#   * $ ACCP_{adj\space preK} = 1.16 \times ACCP_{3mm} - 0.16 \times  K_{preLASIK} $
#   
# * Parameter set 4: $ ACCP_{3mm},\space and\space  K_{preLASIK} $
#   * $ACCP_{adj \space all \space history}=0.95 \times ACCP_{3mm} - 0.196 \times(SE_{postLASIK} - SE_{preLASIK}) +0.053 K_{preLASIK}-  0.128$ 
#   
# * Parameter set 5: $ ACCP_{3mm} $ alone
#   * $ ACCP_{adj \space no \space history}=1.151 \times ACCP_{3mm} - 6.799 $
#   
# * Parameter set 6: SimK alone
#   * $SimK_{adj \space no \space history}=1.114 \times  SimK - 6.062 $

# [Intraocular lens power calculation in eyes with previous corneal refractive surgery](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6053834/) 的作者就看上了前两个参数调整:
# 
# * $ ACCP_{adj}=ACCP_{3mm} - 0.16\times(SE_{postLASIK} - SE_{preLASIK}) =ACCP_{3mm} - 0.16\times SIRC $
# * $ SimK_{adj}= SimK - 0.23 \times (SE_{postLASIK} - SE_{preLASIK})=SimK - 0.23 \times SIRC$

# 如果是远视 
# * $ ACCP_{adj} = ACCP_{3mm} + 0.144 \times SIRC $
# * $ SimK_{adj} = SimK + 0.165 \times SIRC $
# 

# Awwad方法算出来的角膜屈光力, 用修正后的ACCP或者修正后的SimK, 要代入Double-K SRK/T (近视) 或者 Hoffer Q (远视)来计算IOL度数.

# In[20]:


def K_adj(K, SIRC, Ktype="ACCP", Rtype="myopia"):
    parameter={("ACCP","myopia"):-0.16,
               ("SimK","myopia"):-0.23,
               ("ACCP","hyperopia"):+0.144,
               ("SimK","hyperopia"):+0.165,
              }
    return K+parameter[(Ktype,Rtype)]* SIRC


# In[21]:


interact(K_adj,
         K=43,
        SIRC=-3,
        Ktype=["ACCP","SimK"],
        Rtype=["myopia","hyperopia"]);


# ### 临床病史法
# 
# Clinical history method, CHM
# 这是假设角膜屈光手术后的K值Kpost是等于之前的K值Kpre减去切掉的SIRC
# $$
# Kpost = Kpre − SIRC
# $$
# 然后把Kpre, Kpost代入到Double K SRK/T公式里. 但这个方案依赖良好的病历记录.

# In[22]:


def Double_K_SRK_T_CHM(AL, Kpre, SIRC, A,REFt ):
    Kpost= Kpre-SIRC
    return Double_K_SRK_T(AL, Kpre, Kpost, A,REFt )


# In[23]:


interact(Double_K_SRK_T_CHM,
        AL=widgets.FloatText(value=23.5),
        Kpre=widgets.FloatText(value=44),
        A=widgets.FloatText(value=118.4),
        REFt=widgets.FloatText(value=-0.5),
        SIRC=widgets.FloatText(value=-3),
        );


# # 病史数据未知
# 
# 如果完全没有角膜屈光手术前的角膜曲率数据, 也没有屈光状态的改变量, 大概是连病历都找不到的那种.

# * Shammas-PL and PHL formulas:
# $$
# Corneal\space power = 1.14 ∗ Kpost − 6.8
# $$
# 然后要代入Shammas公式. 这个公式不依赖角膜曲率来估计ELP. 所以仅仅就是修正一下K值. 如果仔细看一下Shammas公式的话, 会发现在公式中已经有一步
# ```
# #     KERATOMETRY CORRECTION:  
#     KS = 1.14 * Kpost - 6.8 
# ```
# 所以直接代入Kpost就好了. 

# In[24]:


interact(shammas,
         Kpost=widgets.FloatText(value=43), 
         A=widgets.FloatText(value=118.4), 
         L=widgets.FloatText(value=23),
         R=widgets.FloatText(value=-0.5)
        );


# * Maloney方法:
# 
# K = measured K ∗ 1.114 − 4.90
# 
# 此处不是很明白, 不确定后续应该代入到什么公式里.

# ## Haigis-L 
# Haigis-L公式, 按照这篇文献[Intraocular lens calculation after refractive surgery for myopia: Haigis-L formula](https://www.ncbi.nlm.nih.gov/pubmed/18812114/)的说明,
# 
# 应该是将测量到的角膜中央曲率半径$r_{meas}$, 进行了一番修正, 得到一个$r_{corr}$, 再代入到标准的Haigis公式中
# 
# >Hence, if $r_{meas}$ is the corneal radius (mm) measured with the IOLMaster in an eye after laser surgery for myopia, the corrected radius $r_{corr}$ to be entered into the regular Haigis formula is calculated according to
# 
# $$
# r_{c o r r}=\frac{331.5}{-5.1625 \times r_{m e a s}+82.2603-0.35}
# $$

# In[25]:


interact(Haigis_L,
         R=widgets.FloatText(value=7.45),
         AC=widgets.FloatText(value=2.69),
         L=widgets.FloatText(value=21.44),
         A=widgets.FloatText(value=118.0),
         Rx=widgets.FloatText(value=-0.25), 
         a0=widgets.FloatText(value=1.277),
         a1=widgets.FloatText(value=0.400),
         a2=widgets.FloatText(value=0.100)
        );


# ## Gaussian optics formula
# 
# 这一篇也略喜欢, 按照高斯光学公式, 把角膜看作是有一定厚度的两个面. 是的, 前面的公式其实都忽略了角膜的厚度. 如果算上厚度, 应该是这样的:
# $$
# \mathrm{P}=\frac{\left(\mathrm{n}_{1}-\mathrm{n}_{0}\right)} {\mathrm{r}_{1}}+
#            \frac{\left(\mathrm{n}_{2}-\mathrm{n}_{1}\right)} {\mathrm{r}_{2}}-
#            \frac{\mathrm{d}} {\mathrm{n}_{1}} \times
#            \frac{\left(\mathrm{n}_{1}-\mathrm{n}_{0}\right)}{ \mathrm{r}_{1}}\times
#            \frac{\left(\mathrm{n}_{2}-\mathrm{n}_{1}\right)}{\mathrm{r}_{2}}
#            \tag {3.2}
# $$
# 跟之前的公式比较一下:
# $$
# P=P_a+P_p = \frac{n_2-n_1}{r_1}+\frac{n_3-n_2}{r_2}
# $$
# 
# 发现是多了一组与厚度d有关的项

# 这个公式要测量出角膜前后表面的曲率半径数据, 所以要用Scheimpflug相机的角膜地形图测量设备, 比如PentaCam. 但GOF方式据说有一些误差, 所以Borasio等改善了GOF开发出[BESSt formula](https://sci-hub.tw/10.1016/j.jcrs.2006.08.037).
# 
# BESSt公式, 是根据测量得到的角膜前后表面曲率半径, 重新计算出角膜屈光力, 然后再代入到SRK/T公式, 或者Hoffer Q公式中计算IOL度数. 其中“正常”的眼用SRK/T公式, 眼轴<=22.0mm的使用Hoffer Q公式, 其中还有个细节, SRK/T公式里在计算角膜高度的时候, 有一步开方运算, 被开方是计算出来的角膜宽度, 如果被开方的数小于0, 显然会出错, 在IOL Master中强制=0了. 但在BESSt公式中如果出现被开方小于零的错误, 则切换到Hoffer Q去计算.

# In[27]:


interact(BESST,
         rF=widgets.FloatText(value=7.6),
         rB=widgets.FloatText(value=7.8),
         CCT=widgets.FloatText(value=0.5), 
         AL=widgets.FloatText(value=23), 
         ACD=widgets.FloatText(value=3.5), 
         A=widgets.FloatText(value=118.4),
         Rx=widgets.FloatText(value=-0.5)
        );


# In[ ]:




