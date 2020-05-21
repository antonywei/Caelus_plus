### physical graph
from basic.SFC import SFC
cpuCap = 100
BIGNUM = 100000
class Node(object):
    """docstring for Node"""
    def __init__(self,node_id,connect_nodes,cpu_cap=cpuCap):
        self.id = node_id
        self.connectNodes = connect_nodes ## type dict {Nodes:{info},Nodes:{info}} (direct graph)
        self.cpuCap = cpuCap
        #self.embedVNF = {}
        self.embedSfc = {}  ### type dict {SFC_id:[vnf_id])
        self.sfcList = set()
        self.cpuRe = 1
    def embedVNF(self,sfc_instance,vnf_id):
        cpuConsum = sfc_instance.vnfList[vnf_id][1]
        if(cpuConsum > (self.cpuCap)*(self.cpuRe)):
            print("Cpu limited, can not deploy")
        else:
            if (sfc_instance not in self.sfcList):
                self.embedSfc[sfc_instance.id] = [vnf_id] ## bind vnf id 
                self.sfcList.add(sfc_instance) ## add sfc instance 
            else:
                self.embedSfc[sfc_instance.id].append(vnf_id)
            self.cpuRe = self.cpuRe - cpuConsum/self.cpuCap
            sfc_instance.Mapping_VNF(vnf_id,self.id) ### mapping nodes
            print("embeding VNF: "+str(vnf_id)+" in Node: "+str(self.id)+" success")
    def displayNode(self):
        NodeInfo = {"ID":self.id,"connectNodes":self.connectNodes,\
                    "cpuCap":self.cpuCap,"embedSfc":self.embedSfc, \
                    "cpuRe":self.cpuRe}
        print("***************************Node "+str(self.id)+" info**********************")
        print(NodeInfo)
    def embedCost(self,sfc_instance,vnf_id):
        cpuConsum = sfc_instance.vnfList[vnf_id][1]
        cost = cpuConsum/(self.cpuCap*self.cpuRe)
        if cost < 1:
            return cost
        else:
            return BIGNUM



# a = SFC(sfc_id=1, src=2, dst=3, vnf_list={1:(1,10),2:(2,20)}, bw=2, td=10)
# b = Node(node_id=1,connect_nodes={3:{"linkweight":2},4:{"linkweight":2}})
# b.displayNode()
# b.embedVNF(sfc_instance=a,vnf_id=1)
# b.embedVNF(sfc_instance=a,vnf_id=2)
# b.displayNode()
# a.displaySFC()
