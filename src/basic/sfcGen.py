##SFC GEN
## 1. GEN SFC : SRC DEST VNF 1 2 3 4 5 
## USE sfc.py to generate 

## src, dst is in physical graph 
## input 1.len of SFC; 2. range of cpu; range of bw; range of td;
## return SFC_List
## using pickle to save SFC_list.
from basic.SFC import SFC
import random
from basic.globalvar import *
##         list,              2-tuple, 2-tuple,    2-tuple 2-tuple
def SFC_gen(SFC_id,physical_Node_list=physical_Node_list,CpuRange=CpuRange,\
           LengthRange=LengthRange,BwRange=BwRange,TdRange=TdRange,Length=0):
    SFC_id = SFC_id
    src = physical_Node_list[random.randint(0,len(physical_Node_list)-1)]
    dst = physical_Node_list[random.randint(0,len(physical_Node_list)-1)]
    if Length == 0:
        VNFnum = random.randint(LengthRange[0],LengthRange[1])
    else:
        VNFnum=Length
    VNF_list={i:(i,random.randint(CpuRange[0],CpuRange[1])) for i in range(1,VNFnum)}
    Bw = random.randint(BwRange[0],BwRange[1])
    Td = random.randint(TdRange[0],TdRange[1])
    newSFC = SFC(sfc_id=SFC_id, src=src, dst=dst, vnf_list=VNF_list, bw=Bw, td=Td)
    return newSFC
def gen_SFC_list(SFCnum=SFCnum,LengthRange=LengthRange):
    sfc_list=[]
    for i in range(SFCnum):
        LengthR = LengthRange[1]-LengthRange[0]
        LengthR = SFCnum/LengthR
        newSFC=SFC_gen(SFC_id = i,Length=round((SFCnum-i)/LengthR+LengthRange[0]))


        #### need to modify and make sfc 
        #newSFC.displaySFC()
        sfc_list.append(newSFC)
    return sfc_list




