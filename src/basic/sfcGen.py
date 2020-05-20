##SFC GEN
## 1. GEN SFC : SRC DEST VNF 1 2 3 4 5 
## USE sfc.py to generate 

## src, dst is in physical graph 
## input 1.len of SFC; 2. range of cpu; range of bw; range of td;
## return SFC_List
## using pickle to save SFC_list.
from SFC import SFC
import random
physical_Node_list = [i for i in range(20)]
CpuRange = (20,30)
LengthRange = (3,6) ## VNF numbers range
BwRange = (10,30)
TdRange = (20,40)
SFCnum = 20 
##         list,              2-tuple, 2-tuple,    2-tuple 2-tuple
def SFC_gen(SFC_id,physical_Node_list=physical_Node_list,CpuRange=CpuRange,\
           LengthRange=LengthRange,BwRange=BwRange,TdRange=TdRange):
    SFC_id = SFC_id
    src = physical_Node_list[random.randint(0,len(physical_Node_list)-1)]
    dst = physical_Node_list[random.randint(0,len(physical_Node_list)-1)]
    VNFnum = random.randint(LengthRange[0],LengthRange[1])
    VNF_list={i:(i,random.randint(CpuRange[0],CpuRange[1])) for i in range(1,VNFnum)}
    Bw = random.randint(BwRange[0],BwRange[1])
    Td = random.randint(TdRange[0],TdRange[1])
    newSFC = SFC(SFC_id=SFC_id, src=src, dst=dst, VNF_list=VNF_list, bw=Bw, td=Td)
    return newSFC
def gen_SFC_list(SFCnum=SFCnum):
    SFC_list=[]
    for i in range(SFCnum):
        newSFC=SFC_gen(SFC_id = i)
        newSFC.displaySFC()
        SFC_list.append(newSFC)

A = gen_SFC_list()

