#!/usr/bin/env python
# coding: utf-8

# # Double K 计算

# 参考文献: [Intraocular lens power calculation after corneal refractive surgery: double-K method](sci-hub.tw/10.1016/s0886-3350(03)00957-x)

# The programming was done so that ELP calculation algorithms used Kpre and vergence formula algo- rithms used Kpost. The modified formula is shown in the Appendix. Independent variables were AL, Kpre, Kpost, and the A-constant of the IOL.

# Double-K SRK/T Formula

# In[12]:


import numpy as np


# ## Equation 1: Preoperative corneal radius of curvature:

# $$
# r_{pre} = 337.5/Kpre
# \tag 1
# $$

# In[1]:


def r_pre(K_pre):
    return 337.5/K_pre


# ## Equation 2: Corrected axial length (LCOR):
# 
# If $L \le 24.2$, $ LCOR = L$ 
# 
# If $L \gt 24.2$, $ LCOR = -3.446 + 1.716 \times L - 0.0237 \times L^2$
# 

# In[2]:


def LCOR(L):
    if L <=24.2:
        return L
    else:
        return -3.446+1.716*𝐿-0.0237*(L**2)


# ## Equation 3: Computed corneal width (Cw):
# $$
# Cw = -5.41 + 0.58412 \times LCOR + 0.098 \times Kpre
# \tag 3
# $$

# In[9]:


def Cw(L, K_pre):
    return -5.41+0.58412* LCOR(L)+0.098*K_pre


# ## Equation 4: Corneal height (H):
# $$
# H = r_{pre} - \sqrt {r_{pre}2 - (Cw2/4)}
# \tag {4.0}
# $$
# 原文如上, 但$r_{pre}2 - (Cw2/4)$ 看起来很诡异, 估计是平方项的打印错误. 故修改成
# $$
# H = r_{pre} - \sqrt {r_{pre}^2 - (Cw^2/4)}
# \tag {4.1}
# $$

# In[26]:


def H(L, K_pre):
    r=r_pre(K_pre)
    c=Cw(L,K_pre)
    rc=r**2-(c**2/4) if (r**2-(c**2/4))>=0 else 0
    return r-np.sqrt(r**2-(c**2/4))
    


# ## Equation 5: Offset value:
# $$
# \text { Offset }=\mathrm{ACD}_{\text {const }}-3.336
# \tag 5
# $$

# In[15]:


def offset(ACD_const):
    return ACD_const-3.336


# ## Equation 6: Estimated postoperative ELP (ACD):
# $$
# \mathrm{ACD}_{\mathrm{est}}=\mathrm{H}+\text { Offset }
# \tag 6
# $$

# In[16]:


def ACD_est(L,K_pre, ACD_const):
    return H(L,K_pre)+offset(ACD_const)


# ## Equation 7: Constants:
# $$
# \mathrm{V}=12 ; \mathrm{n}_{\mathrm{a}}=1.336 ; \mathrm{n}_{\mathrm{c}}=1.333 ; \mathrm{n}_{\mathrm{c}} \mathrm{m} 1=0.333
# \tag 7
# $$

# In[19]:


def get_constants():
    constants["V"]=12
    constants["n_a"]=1.336
    constants["n_c"]=1.333
    constants["n_c_m1"]=0.333 #n_c minus 1
    return constants


# ## Equation 8: Retinal thickness (RETHICK) and optical axial length (LOPT):
# $$
# \begin{array}{c}{\mathrm{RETHCK}=0.65696-0.02029 \times \mathrm{L}} \\ {\mathrm{LOPT}=\mathrm{L}+\mathrm{RETHICK}}\end{array}
# \tag 8
# $$

# In[20]:


def RETHICK(L):
    return 0.65696 - 0.02029*L
def LOPT(L):
    return L+RETHICK(L)


# ## Equation 9: Postoperative corneal radius of curvature:
# $$
# \mathrm{r}_{\mathrm{post}}=337.5 / \mathrm{Kpost}
# \tag 9
# $$

# In[21]:


def r_post(K_post):
    return 337.5/K_post


# ## Equation 10: Emmetropia IOL power (IOLemme):
# ![](https://cdn.mathpix.com/snip/images/DNc7H0lZaoQr2q_JkxvlJ-D7fF0VV7qTpijZ3ygemls.original.fullsize.png)

# $$
# IOL_{emme}= \frac {1000 \times n_a \times ( n \times r_{post} -n_cm1 \times LOPT)} {(LOPT-ACD_{est}) \times (n_a \times r_{post} -n_cm1 \times ACD_{est})}
# $$

# In[ ]:


def S(L,K_pre,K_post,ACD_const):
    S1=LOPT()-ACD_est
    S2=n_a*r_post-c2*ACD_est
    S3=n_a*r_post-c2*LOPT
    S4=V*S3+LOPT*r_post
    S5=V*S2+ACD_est*r_post


# In[25]:


def IOL_emme(L,K_pre,K_post,ACD_const):
    constants=get_constants()
    n_a=constants["n_a"]
    n = constants["n_a"] # who knows what is n ??? 
    n_cm1=constants["n_cm1"]
    numerator=1000*n_a*( n*r_post(K_post) -n_cm1*LOPT(L) )
    denominator=( LOPT(L)-ACD_est(L,K_pre, ACD_const) ) *                 (n_a*r_post(K_post) -n_cm1*ACD_est(L,K_pre, ACD_const) )
    return numerator/denominator


# In[ ]:




