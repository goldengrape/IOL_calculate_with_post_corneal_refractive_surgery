#!/usr/bin/env python
# coding: utf-8

# # IOL 计算

# In[4]:


import numpy as np


# In[16]:


def Double_K_SRK_T(AL, Kpre, Kpost, A,REFt ):
#   Correction Axial Length: Lcor
    Lcor = AL if AL<=24.2 else (-3.446 + (1.716 * AL) - (0.0237 * AL**2))
#   Corneal curvatures, 2 Keratometry values are used:  
#   Pre corneal refractive surgery:
    Rpre = 337.5 / Kpre 
    # Kpre = 337.5 / Rpre
#   Post corneal refractive surgery:  
    Rpost = 337.5 / Kpost   
    # Kpost = 337.5 / Rpost
#   Calculations with Kpre or Rpre:  
#   Computed corneal width: CW    
    CW = -5.40948 + 0.58412 * Lcor + 0.098 * Kpre
#   Corneal Height: H 
    Rc = (Rpre**2 - CW**2 / 4) 
    Rc = 0 if Rc<0 else Rc
    H = Rpre - np.sqrt(Rc)
#   Anterior Chamber Depth Constant: ACDconst  
    ACDconst = 0.62467 * A - 68.74709
#   Estimated Post-operatice ACD: ACDest   
    Offset = ACDconst - 3.3357
    ACDest = H + Offset
#   Constants: 
    na = 1.336; V = 12; nc = 1.333; C2 = nc -  1
#   Retinal thickness:  
    Rethick = 0.65696 - 0.02029 * AL
#   Optical Axial Length: 
    L0PT = AL + Rethick   
#   Calculations with Kpost or Rpost: 
    S1 = L0PT - ACDest 
    S2 = na * Rpost - C2 * ACDest 
    S3 = na * Rpost - C2 * L0PT  
    S4 = V * S3 + L0PT * Rpost 
    S5 = V * S2 + ACDest * Rpost
    
    IOL_emme= 1336 * S3 / (S1*S2)
#     REF_X=(1336* S3- IOL* S1* S2)/(1.336*S4-0.001*IOL*S1*S5)
    IOL_for_tgt=(1336* (S3-0.001*REFt*S4))/                 (S1*(S2-0.001*REFt*S5))
    return IOL_for_tgt


# In[22]:


def SRK_T(AL,Kd,A,REFt):
#     Retinal thickness: 
    Rethick = 0.65696 - 0.02029 * AL
    Lc = AL if (AL <= 24.2) else (-3.446 + (1.716 * AL) - (0.0237 * AL**2 ) )
#     Kd = 337.5 / Rmm 
    Rmm = 337.5 / Kd
    C1 = -5.40948 + 0.58412 * Lc + 0.098 * Kd
    Rc = Rmm**2 - (C1**2) / 4 
    Rc = 0 if Rc < 0 else Rc
    C2 = Rmm - np.sqrt(Rc)
    ACD = 0.62467 * A - 68.74709
    ACDE = C2 + ACD - 3.3357
    n1 = 1.336
    n2 = 0.333
    L0 = AL + Rethick
    S1 = L0 - ACDE     
    S2 = n1 * Rmm - n2 * ACDE  
    S3 = n1 * Rmm - n2 * L0   
    S4 = 12 * S3 + L0 * Rmm  
    S5 = 12 * S2 + ACDE * Rmm
#     REF_X = (1336 * S3 −  IOL * S1 * S2)/ \
#             (1.336 * S4 −  0.001 * IOL * S1 * S5)
    IOL_FOR_TGT =(1336 * (S3 -  0.001 * REFt * S4))/                  (S1 * (S2 -  0.001 * REFt * S5))
    return IOL_FOR_TGT


# In[42]:


def HOFFER_Q(AL, K, ACD, Rx):
    def tan(x):
        x=np.radians(x)
        return np.tan(x)
#     CORRECTED CHAMBER DEPTH
    if AL<=23:
        M = +1; G = 28 
    elif AL > 23:
        M =-1;  G=23.5
    if AL > 31:
        AL = 31 
    elif AL < 18.5:
        AL = 18.5
    
    CD = ACD + 0.3* (AL - 23.5) 
    CD += (tan(K))**2
    CD += 0.1*M*(23.5-AL)** 2*tan(0.1*(G - AL)**2) - 0.99166
#     EMMETROPIA POWER:
    R = Rx / (1 - 0.012 * Rx)  
    P = (1336 / (AL - CD - 0.05)) - (1.336 / ((1.336 / (K + R)) - ((CD + 0.05) / 1000)))
    return P
                                     

