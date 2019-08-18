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


# In[108]:


def SRK_T_Rc(AL, Kd,A,REFt):
    #  Retinal thickness: 
    Rethick = 0.65696 - 0.02029 * AL
    Lc = AL if (AL <= 24.2) else (-3.446 + (1.716 * AL) - (0.0237 * AL**2 ) )
#     Kd = 337.5 / Rmm 
    Rmm = 337.5 / Kd
    C1 = -5.40948 + 0.58412 * Lc + 0.098 * Kd
    Rc = Rmm**2 - (C1**2) / 4 
    return Rc


# In[109]:


def SRK_T(AL,Kd,A,REFt):
#     Retinal thickness: 
    Rethick = 0.65696 - 0.02029 * AL
    Lc = AL if (AL <= 24.2) else (-3.446 + (1.716 * AL) - (0.0237 * AL**2 ) )
#     Kd = 337.5 / Rmm 
    Rmm = 337.5 / Kd
    C1 = -5.40948 + 0.58412 * Lc + 0.098 * Kd
    Rc = Rmm**2 - (C1**2) / 4 
    Rc = 0 if SRK_T_Rc(AL, Kd,A,REFt) < 0 else Rc
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
                                     


# In[48]:


def shammas(Kpost,L, A, R):
#     https://sci-hub.tw/10.1016/j.jcrs.2006.08.045
#     KERATOMETRY CORRECTION:  
    KS = 1.14 * Kpost - 6.8 
#     Where Kpost is the measurement of the Keratometry by classical means.
    C =  0.5835*A - 64.40 # ACD (Shammas) =
#     FORMULA TO CALCULATE THE IMPLANT CORRESPONDING TO THE DESIRED REFRACTION (R):
    K=KS
    IOLAm = 1336 / (L -  0.1* (L -  23) -  C - 0.05) -             1 /( 1.0125/ (K + R) -  (C +  0.05) / 1336 )
    return IOLAm


# In[87]:


def Haigis(R,AC,L,A,Rx, a0=None,a1=0.400,a2=0.100):
#     IOL power for given refraction Dl:  All calculations are based on the "Thin-lens-formula":
#     Dl  IOL power 
#     Dc  corneal power 
#     Rx  desired refraction 
#     n  refractive index of aequeous and vitreous (=1.366) # here should be 1.336
#     Nc  fictitious refractive index of cornea (=1.3315) 
#     Dx  vertex distance between cornea and spectacles (=12 mm) 
#     R  corneal radius 
#     L  axial length (as measured by ultrasound) 
#     d  optical ACD

#     AC : preoperative acoustical anterior chamber depth, as measured by ultrasound    
#     L: preoperative axial length, as measured by ultrasound
    if a0==None:
        a0=0.62467 * A - 72.434
    u = -0.241  
    v = 0.139
    if AC==0:
        d = (a0 + u*a1) + (a2 + v*a1)*L  
    else:
        d = a0 +a1*AC + a2*L
    n=1.336; Nc=1.3315; 
    # convert mm to meter
    Dx=12/1000;
    R=R/1000
    AC=AC/1000
    L=L/1000
    d=d/1000
    
    Dc=(Nc-1)/(R)
    z=Dc+Rx/(1-Rx*Dx)
    Dl=n/(L-d) - n/ (n/z -d)
    
    return Dl


# In[95]:


def Haigis_L(R,AC,L,A,Rx, a0=None,a1=0.400,a2=0.100):
    R_corr=331.5/(-5.1625*R+82.2603-0.35)
    return Haigis(R_corr,AC,L,A,Rx,a0,a1,a2)


# In[106]:


def BESST(rF,rB,CCT, AL, ACD, A,Rx):
#     https://sci-hub.tw/10.1016/j.jcrs.2006.08.037
    n_air=1
    n_vc=1.3265
    n_CCT=n_vc+(CCT*0.000022)
    k_conv=337.5/rF
    if  k_conv<37.5:
        n_adj=n_CCT+0.017
    elif k_conv<41.44:
        n_adj=n_CCT
    elif k_conv<45:
        n_adj=n_CCT-0.015
    else:
        n_adj=n_CCT
    n_acq= 1.336
    d_cct=CCT/1000000
    d=d_cct/n_vc
    Fant=1/rF*(n_vc-n_air)
    Fpost=1/rB*(n_acq-n_vc)
    
#   corneal power in virgin corneas[D]
    BESSt_vc_K=((1/rF*(n_vc-n_air))
                +(1/rB*(n_acq-n_vc))
                -(d*1/rF*(n_vc-n_air)
                *1/rB*(n_acq-n_vc)))*1000
#   corneal power after keratorefractive surgery[D]
    BESSt_K=((1/rF*(n_adj-n_air))
             +(1/rB*(n_acq-n_adj))
             -(d*1/rF*(n_adj-n_air)
               *1/rB*(n_acq-n_adj)))*1000
    

    K=BESSt_K
    
    if (AL<=22.0 or SRK_T_Rc(AL, K,A,Rx)<=0):
        IOL=HOFFER_Q(AL, K, ACD, Rx)
    else:
        IOL=SRK_T(AL,K,A,Rx)
    
    return IOL   


# In[ ]:




